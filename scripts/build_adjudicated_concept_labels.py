import argparse
import json
from pathlib import Path
from typing import Any

from app.ontology.service import OntologyService
from scripts.prepare_concept_second_review import load_all_audit_overrides


def build_adjudicated_labels(
    datasets: list[Path],
    audit_paths: list[Path],
    reference_key_path: Path,
    reconciliation_path: Path,
    adjudication_path: Path,
    active_concepts: set[str],
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in datasets:
        for source in json.loads(path.read_text(encoding="utf-8")):
            question_id = str(source["source_question_id"])
            if question_id in seen:
                raise ValueError(f"Duplicate source_question_id: {question_id}")
            seen.add(question_id)
            examples.append(dict(source))

    audit_overrides = load_all_audit_overrides(audit_paths)
    unknown_audits = sorted(set(audit_overrides) - seen)
    if unknown_audits:
        raise ValueError(f"Audit labels do not match datasets: {unknown_audits}")
    for example in examples:
        question_id = str(example["source_question_id"])
        if question_id in audit_overrides:
            example["gold_concepts"] = audit_overrides[question_id]

    reference_payload = json.loads(reference_key_path.read_text(encoding="utf-8"))
    question_by_review = {
        str(item["review_id"]): str(item["source_question_id"])
        for item in reference_payload["items"]
    }
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    expected = {str(item["review_id"]) for item in reconciliation["disagreements"]}
    adjudication = json.loads(adjudication_path.read_text(encoding="utf-8"))
    decisions = adjudication["adjudications"]
    decision_ids = [str(item["review_id"]) for item in decisions]
    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError("Duplicate adjudication review ID")
    if set(decision_ids) != expected:
        raise ValueError("Adjudication IDs must exactly match reconciliation disagreements")

    final_overrides: dict[str, list[str]] = {}
    for decision in decisions:
        review_id = str(decision["review_id"])
        labels = list(decision["adjudicated_concepts"])
        unknown = sorted(set(labels) - active_concepts)
        if unknown:
            raise ValueError(f"{review_id}: inactive adjudicated concepts {unknown}")
        final_overrides[question_by_review[review_id]] = labels

    for example in examples:
        question_id = str(example["source_question_id"])
        if question_id in final_overrides:
            example["gold_concepts"] = final_overrides[question_id]
        example["review_status"] = "llm_adjudicated_not_human_gold"
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(description="Build adjudicated concept labels")
    parser.add_argument("--dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--selection-dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--label-audit", type=Path, nargs="+", required=True)
    parser.add_argument("--reference-key", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--selection-output", type=Path, required=True)
    args = parser.parse_args()

    active = OntologyService().vocabulary_concept_names()
    examples = build_adjudicated_labels(
        args.dataset,
        args.label_audit,
        args.reference_key,
        args.reconciliation,
        args.adjudication,
        active,
    )
    selection_ids = {
        str(item["source_question_id"])
        for path in args.selection_dataset
        for item in json.loads(path.read_text(encoding="utf-8"))
    }
    selection = [
        example
        for example in examples
        if str(example["source_question_id"]) in selection_ids
    ]
    if len(selection) != len(selection_ids):
        raise ValueError("Not every selection question was found in adjudicated labels")
    for path, payload in ((args.output, examples), (args.selection_output, selection)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    summary = {
        "questions": len(examples),
        "positive_questions": sum(bool(item["gold_concepts"]) for item in examples),
        "selection_questions": len(selection),
        "selection_positive_questions": sum(
            bool(item["gold_concepts"]) for item in selection
        ),
        "status": "llm_adjudicated_not_human_gold",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
