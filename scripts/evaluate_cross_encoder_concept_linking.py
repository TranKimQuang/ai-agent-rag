import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.models import ConceptLinkingMethod
from app.ontology.service import CrossEncoderConceptCandidate, OntologyService
from app.rag.reranker import SentenceTransformerCrossEncoderReranker
from app.rag.retriever import SentenceTransformerEncoder


def metrics(
    examples: list[dict[str, Any]], predictions: list[set[str]]
) -> dict[str, float]:
    true_positive = 0
    predicted_total = 0
    gold_total = 0
    exact = 0
    for example, predicted in zip(examples, predictions, strict=True):
        gold = set(example["gold_concepts"])
        true_positive += len(gold & predicted)
        predicted_total += len(predicted)
        gold_total += len(gold)
        exact += int(gold == predicted)
    precision = true_positive / predicted_total if predicted_total else 0.0
    recall = true_positive / gold_total if gold_total else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        ),
        "exact_match": exact / len(examples) if examples else 0.0,
    }


def predict(
    service: OntologyService,
    text: str,
    candidates: list[CrossEncoderConceptCandidate],
    *,
    cross_threshold: float,
    cross_margin: float,
    limit: int,
) -> set[str]:
    exact = service.link_concepts(
        text,
        ConceptLinkingMethod.ALIAS,
        threshold=service.query_linking_threshold,
        limit=limit,
    )
    selected = {link.concept for link in exact}
    semantic_threshold = service.query_linking_threshold + (0.05 if exact else 0.0)
    by_phrase: dict[str, list[CrossEncoderConceptCandidate]] = defaultdict(list)
    for candidate in candidates:
        if candidate.link.score >= semantic_threshold:
            by_phrase[candidate.phrase].append(candidate)
    accepted: list[CrossEncoderConceptCandidate] = []
    for phrase_candidates in by_phrase.values():
        ranked = sorted(
            phrase_candidates,
            key=lambda candidate: candidate.cross_score,
            reverse=True,
        )
        best = ranked[0]
        runner_up = ranked[1].cross_score if len(ranked) > 1 else float("-inf")
        if (
            best.cross_score >= cross_threshold
            and best.cross_score - runner_up >= cross_margin
        ):
            accepted.append(best)
    accepted.sort(key=lambda candidate: candidate.cross_score, reverse=True)
    for candidate in accepted:
        if len(selected) >= limit:
            break
        selected.add(candidate.link.concept)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibrate cross-encoder re-ranking for ontology concept candidates"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--semantic-threshold", type=float, default=0.55)
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--link-limit", type=int, default=5)
    parser.add_argument(
        "--cross-thresholds",
        type=float,
        nargs="+",
        default=[-4.0, -2.0, 0.0, 2.0, 4.0],
    )
    parser.add_argument(
        "--cross-margins",
        type=float,
        nargs="+",
        default=[0.0, 0.5, 1.0, 2.0],
    )
    args = parser.parse_args()

    examples = json.loads(args.dataset.read_text(encoding="utf-8"))
    service = OntologyService(
        semantic_encoder=SentenceTransformerEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        query_linking_threshold=args.semantic_threshold,
        query_phrase_linking=True,
    )
    scorer = SentenceTransformerCrossEncoderReranker(device="cpu")
    candidates = [
        service.cross_encoder_query_candidates(
            example["text"],
            scorer,
            semantic_threshold=args.semantic_threshold,
            candidate_limit=args.candidate_limit,
        )
        for example in examples
    ]
    phrase_first_predictions = [
        {link.concept for link in service.link_query_concepts(example["text"])}
        for example in examples
    ]

    configurations = []
    predictions_by_configuration: dict[tuple[float, float], list[set[str]]] = {}
    for threshold, margin in itertools.product(
        args.cross_thresholds, args.cross_margins
    ):
        predictions = [
            predict(
                service,
                example["text"],
                example_candidates,
                cross_threshold=threshold,
                cross_margin=margin,
                limit=args.link_limit,
            )
            for example, example_candidates in zip(examples, candidates, strict=True)
        ]
        result = metrics(examples, predictions)
        configurations.append(
            {"cross_threshold": threshold, "cross_margin": margin, **result}
        )
        predictions_by_configuration[(threshold, margin)] = predictions

    configurations.sort(
        key=lambda row: (
            -row["f1"],
            -row["precision"],
            -row["exact_match"],
            row["cross_threshold"],
            row["cross_margin"],
        )
    )
    best = configurations[0]
    best_predictions = predictions_by_configuration[
        (best["cross_threshold"], best["cross_margin"])
    ]
    rows = []
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
                        "cross_score": candidate.cross_score,
                    }
                    for candidate in example_candidates
                ],
            }
        )
    payload = {
        "dataset": str(args.dataset),
        "semantic_threshold": args.semantic_threshold,
        "candidate_limit": args.candidate_limit,
        "link_limit": args.link_limit,
        "reranker_model": scorer.model_name,
        "selection_policy": "highest F1, then precision, exact match, threshold and margin",
        "phrase_first_baseline": metrics(examples, phrase_first_predictions),
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
