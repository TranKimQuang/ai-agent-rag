import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.models import ConceptLinkingMethod
from app.ontology.nli import DEFAULT_NLI_MODEL, SentenceTransformerNliScorer
from app.ontology.service import CrossEncoderConceptCandidate, OntologyService
from app.rag.retriever import SentenceTransformerEncoder
from scripts.evaluate_cross_encoder_concept_linking import metrics
from scripts.run_concept_linking_benchmark import load_examples, validate_gold_concepts


def predict_nli(
    service: OntologyService,
    text: str,
    candidates: list[CrossEncoderConceptCandidate],
    *,
    entailment_threshold: float,
    entailment_margin: float,
    limit: int,
) -> set[str]:
    """Keep exact aliases and NLI-supported semantic candidates."""
    exact = service.link_concepts(
        text,
        ConceptLinkingMethod.ALIAS,
        threshold=service.query_linking_threshold,
        limit=limit,
    )
    selected = {link.concept for link in exact}
    by_phrase: dict[str, list[CrossEncoderConceptCandidate]] = defaultdict(list)
    for candidate in candidates:
        by_phrase[candidate.phrase].append(candidate)

    supported: dict[str, CrossEncoderConceptCandidate] = {}
    for phrase_candidates in by_phrase.values():
        ranked = sorted(
            phrase_candidates,
            key=lambda candidate: candidate.cross_score,
            reverse=True,
        )
        best = ranked[0]
        runner_up = ranked[1].cross_score if len(ranked) > 1 else 0.0
        if (
            best.cross_score < entailment_threshold
            or best.cross_score - runner_up < entailment_margin
        ):
            continue
        previous = supported.get(best.link.concept)
        if previous is None or best.cross_score > previous.cross_score:
            supported[best.link.concept] = best

    for candidate in sorted(
        supported.values(), key=lambda item: item.cross_score, reverse=True
    ):
        if len(selected) >= limit:
            break
        selected.add(candidate.link.concept)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibrate an NLI gate for ontology concept candidates"
    )
    parser.add_argument("--dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--label-audit", type=Path, nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_NLI_MODEL)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--link-limit", type=int, default=5)
    parser.add_argument(
        "--entailment-thresholds",
        type=float,
        nargs="+",
        default=[0.40, 0.50, 0.60, 0.70, 0.80],
    )
    parser.add_argument(
        "--entailment-margins",
        type=float,
        nargs="+",
        default=[0.00, 0.05, 0.10, 0.20],
    )
    args = parser.parse_args()

    examples = load_examples(args.dataset, label_audits=args.label_audit)
    service = OntologyService(
        semantic_encoder=SentenceTransformerEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        query_linking_threshold=0.55,
        query_phrase_linking=True,
    )
    validate_gold_concepts(service, examples)
    scorer = SentenceTransformerNliScorer(args.model, device=args.device)
    candidates = [
        service.cross_encoder_query_candidates(
            example["text"],
            scorer,
            semantic_threshold=0.0,
            candidate_limit=args.candidate_limit,
        )
        for example in examples
    ]
    baseline_predictions = [
        {link.concept for link in service.link_query_concepts(example["text"])}
        for example in examples
    ]

    configurations: list[dict[str, float]] = []
    predictions_by_configuration: dict[tuple[float, float], list[set[str]]] = {}
    for threshold, margin in itertools.product(
        args.entailment_thresholds, args.entailment_margins
    ):
        predictions = [
            predict_nli(
                service,
                example["text"],
                example_candidates,
                entailment_threshold=threshold,
                entailment_margin=margin,
                limit=args.link_limit,
            )
            for example, example_candidates in zip(examples, candidates, strict=True)
        ]
        result = metrics(examples, predictions)
        configurations.append(
            {"entailment_threshold": threshold, "entailment_margin": margin, **result}
        )
        predictions_by_configuration[(threshold, margin)] = predictions

    configurations.sort(
        key=lambda row: (
            -row["f1"],
            -row["precision"],
            -row["exact_match"],
            row["entailment_threshold"],
            row["entailment_margin"],
        )
    )
    best = configurations[0]
    best_predictions = predictions_by_configuration[
        (best["entailment_threshold"], best["entailment_margin"])
    ]
    rows: list[dict[str, Any]] = []
    for example, prediction, example_candidates in zip(
        examples, best_predictions, candidates, strict=True
    ):
        rows.append(
            {
                "source_question_id": example.get("source_question_id"),
                "text": example["text"],
                "gold_concepts": example["gold_concepts"],
                "predicted_concepts": sorted(prediction),
                "candidates": [
                    {
                        "phrase": candidate.phrase,
                        "concept": candidate.link.concept,
                        "semantic_score": candidate.link.score,
                        "entailment_probability": candidate.cross_score,
                    }
                    for candidate in example_candidates
                ],
            }
        )
    payload = {
        "datasets": [str(path) for path in args.dataset],
        "label_audits": [str(path) for path in args.label_audit],
        "candidate_policy": "semantic Top-K without acceptance threshold, then NLI gate",
        "nli_model": scorer.model_name,
        "nli_label_order": ["contradiction", "entailment", "neutral"],
        "selection_policy": "highest F1, then precision, exact match, threshold and margin",
        "phrase_first_baseline": metrics(examples, baseline_predictions),
        "best": best,
        "configurations": configurations,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "phrase_first_baseline": payload["phrase_first_baseline"],
                "best": best,
                "top_five": configurations[:5],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
