import argparse
import json
from pathlib import Path

from app.evaluation.concept_linking import (
    ConceptLinkingExample,
    evaluate_concept_linking_with_rows,
)
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder


def load_examples(paths: list[Path]) -> list[ConceptLinkingExample]:
    examples: list[ConceptLinkingExample] = []
    seen_ids: set[str] = set()
    for path in paths:
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            source_id = str(row.get("source_question_id", ""))
            if source_id and source_id in seen_ids:
                raise ValueError(f"Duplicate source_question_id: {source_id}")
            if source_id:
                seen_ids.add(source_id)
            examples.append(row)
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ontology concept-linking methods")
    parser.add_argument(
        "--dataset",
        type=Path,
        nargs="+",
        default=[Path("evaluation/concept_linking_sample.json")],
        help="One or more disjoint labelled concept-linking datasets.",
    )
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
        help="Semantic thresholds to compare on the validation labels.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/concept_linking_benchmark.json"),
    )
    args = parser.parse_args()

    examples = load_examples(args.dataset)
    service = OntologyService(semantic_encoder=SentenceTransformerEncoder())
    detailed_by_threshold = {
        f"{threshold:.2f}": evaluate_concept_linking_with_rows(
            service,
            examples,
            threshold=threshold,
        )
        for threshold in sorted(set(args.thresholds))
    }
    by_threshold = {
        threshold: details["results"]
        for threshold, details in detailed_by_threshold.items()
    }
    selected_threshold = max(
        by_threshold,
        key=lambda threshold: (
            by_threshold[threshold]["hybrid"]["f1"],
            by_threshold[threshold]["hybrid"]["precision"],
            by_threshold[threshold]["semantic"]["f1"],
            -float(threshold),
        ),
    )
    results = {
        "datasets": [str(path) for path in args.dataset],
        "selection_metric": "hybrid_f1",
        "selected_threshold": float(selected_threshold),
        "selected_results": by_threshold[selected_threshold],
        "selected_predictions": detailed_by_threshold[selected_threshold]["rows"],
        "by_threshold": by_threshold,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
