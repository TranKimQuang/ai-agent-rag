import argparse
import json
from pathlib import Path

from app.evaluation.concept_linking import (
    ConceptLinkingExample,
    evaluate_concept_linking_with_rows,
)
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder


def load_label_overrides(paths: list[Path]) -> dict[str, list[str]]:
    """Load audited label corrections without mutating the source review files."""
    overrides: dict[str, list[str]] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for correction in payload.get("corrections", []):
            source_id = str(correction["source_question_id"])
            if source_id in overrides:
                raise ValueError(f"Duplicate label override: {source_id}")
            overrides[source_id] = list(correction["audited_concepts"])
    return overrides


def load_examples(
    paths: list[Path], *, label_audits: list[Path] | None = None
) -> list[ConceptLinkingExample]:
    examples: list[ConceptLinkingExample] = []
    seen_ids: set[str] = set()
    overrides = load_label_overrides(label_audits or [])
    for path in paths:
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            source_id = str(row.get("source_question_id", ""))
            if source_id and source_id in seen_ids:
                raise ValueError(f"Duplicate source_question_id: {source_id}")
            if source_id:
                seen_ids.add(source_id)
            item = dict(row)
            if source_id in overrides:
                item["gold_concepts"] = overrides[source_id]
            examples.append(item)  # type: ignore[arg-type]
    unused = sorted(set(overrides) - seen_ids)
    if unused:
        raise ValueError(f"Label overrides do not match loaded examples: {unused}")
    return examples


def validate_gold_concepts(
    service: OntologyService, examples: list[ConceptLinkingExample]
) -> None:
    """Reject benchmark labels that the active linker can never predict."""
    active = service.vocabulary_concept_names()
    invalid: dict[str, list[str]] = {}
    for index, example in enumerate(examples):
        unknown = sorted(set(example["gold_concepts"]) - active)
        if unknown:
            source_id = str(example.get("source_question_id") or f"row-{index + 1}")
            invalid[source_id] = unknown
    if invalid:
        raise ValueError(
            "Gold concepts are absent from the active linker vocabulary: "
            + json.dumps(invalid, ensure_ascii=False, sort_keys=True)
        )


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
        "--label-audit",
        type=Path,
        nargs="*",
        default=[],
        help="Audit JSON files whose corrections override labels by source_question_id.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/concept_linking_benchmark.json"),
    )
    args = parser.parse_args()

    examples = load_examples(args.dataset, label_audits=args.label_audit)
    service = OntologyService(semantic_encoder=SentenceTransformerEncoder())
    validate_gold_concepts(service, examples)
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
