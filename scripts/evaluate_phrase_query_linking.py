import argparse
import json
from pathlib import Path
from typing import Any

from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder
from scripts.run_concept_linking_benchmark import load_examples


def score_predictions(
    examples: list[dict[str, Any]], predictions: list[set[str]]
) -> dict[str, float]:
    true_positive = 0
    predicted_total = 0
    gold_total = 0
    exact_matches = 0
    for example, predicted in zip(examples, predictions, strict=True):
        gold = set(example["gold_concepts"])
        true_positive += len(predicted & gold)
        predicted_total += len(predicted)
        gold_total += len(gold)
        exact_matches += int(predicted == gold)
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
        "exact_match": exact_matches / len(examples) if examples else 0.0,
        "linked_examples": sum(bool(prediction) for prediction in predictions),
        "examples": len(examples),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare whole-query and phrase-first ontology concept linking"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        nargs="+",
        required=True,
        help="One or more disjoint labelled concept-linking datasets.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--margin", type=float, default=0.03)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    examples = load_examples(args.dataset)
    service = OntologyService(
        semantic_encoder=SentenceTransformerEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        query_linking_threshold=args.threshold,
        linking_limit=args.limit,
        query_phrase_linking=True,
        query_phrase_margin=args.margin,
    )
    texts = [example["text"] for example in examples]
    baseline_links = service.link_concepts_batch(
        texts,
        ConceptLinkingMethod.HYBRID,
        threshold=args.threshold,
        limit=args.limit,
    )
    phrase_links = [service.link_query_concepts(text) for text in texts]
    baseline_predictions = [
        {link.concept for link in links} for links in baseline_links
    ]
    phrase_predictions = [{link.concept for link in links} for links in phrase_links]

    rows = []
    for example, baseline, phrase, links in zip(
        examples,
        baseline_predictions,
        phrase_predictions,
        phrase_links,
        strict=True,
    ):
        rows.append(
            {
                "source_question_id": example.get("source_question_id"),
                "text": example["text"],
                "gold_concepts": example["gold_concepts"],
                "baseline_concepts": sorted(baseline),
                "phrase_concepts": sorted(phrase),
                "phrase_details": [link.model_dump(mode="json") for link in links],
                "changed": baseline != phrase,
            }
        )

    payload = {
        "datasets": [str(path) for path in args.dataset],
        "threshold": args.threshold,
        "top1_top2_margin": args.margin,
        "limit": args.limit,
        "baseline": score_predictions(examples, baseline_predictions),
        "phrase_first": score_predictions(examples, phrase_predictions),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({key: payload[key] for key in ("baseline", "phrase_first")}, indent=2))


if __name__ == "__main__":
    main()
