import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from rdflib.namespace import SKOS

from app.ontology.service import QA, OntologyService
from scripts.run_concept_linking_benchmark import load_label_overrides


def load_all_audit_overrides(paths: list[Path]) -> dict[str, list[str]]:
    """Load corrections and fully enumerated audit items into one label overlay."""
    overrides: dict[str, list[str]] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries = [*payload.get("corrections", []), *payload.get("items", [])]
        for entry in entries:
            question_id = str(entry["source_question_id"])
            labels = list(entry["audited_concepts"])
            previous = overrides.get(question_id)
            if previous is not None and previous != labels:
                raise ValueError(f"Conflicting audit labels: {question_id}")
            overrides[question_id] = labels
    return overrides


def build_review_rows(
    datasets: list[Path],
    audit_paths: list[Path],
    evidence_path: Path,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence_by_id = {
        str(row["question_id"]): row for row in evidence_payload["questions"]
    }
    generic_overrides = load_label_overrides(
        [path for path in audit_paths if "positive_label_audit" not in path.name]
    )
    overrides = {**generic_overrides, **load_all_audit_overrides(audit_paths)}
    rows: list[dict[str, str]] = []
    keys: list[dict[str, Any]] = []
    seen: set[str] = set()
    source_rows: list[dict[str, Any]] = []
    for path in datasets:
        source_rows.extend(json.loads(path.read_text(encoding="utf-8")))
    source_rows.sort(
        key=lambda row: hashlib.sha256(
            str(row["source_question_id"]).encode("utf-8")
        ).hexdigest()
    )
    for number, source in enumerate(source_rows, start=1):
        question_id = str(source["source_question_id"])
        if question_id in seen:
            raise ValueError(f"Duplicate source_question_id: {question_id}")
        seen.add(question_id)
        context = evidence_by_id.get(question_id)
        if context is None:
            raise ValueError(f"Missing evidence context: {question_id}")
        labels = overrides.get(question_id, list(source["gold_concepts"]))
        review_id = f"CR-{number:03d}"
        rows.append(
            {
                "review_id": review_id,
                "paper_id": str(context["document_id"]),
                "question": str(source["text"]),
                "gold_evidence_excerpt": str(context["gold_evidence_excerpt"]),
                "reviewer_concepts": "",
                "reviewer_none": "",
                "reviewer_notes": "",
            }
        )
        keys.append(
            {
                "review_id": review_id,
                "source_question_id": question_id,
                "audited_concepts": labels,
            }
        )
    return rows, keys


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_concept_catalog(path: Path) -> None:
    service = OntologyService()
    rows = []
    for name in sorted(service.vocabulary_concept_names()):
        concept = QA[name]
        definitions = [str(value) for value in service.graph.objects(concept, SKOS.definition)]
        rows.append(
            {
                "concept_id": name,
                "preferred_label": service.preferred_label(concept),
                "definition": " ".join(definitions),
            }
        )
    write_csv(path, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a blinded second-review packet")
    parser.add_argument("--dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--label-audit", type=Path, nargs="+", required=True)
    parser.add_argument("--evidence-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--key-output", type=Path, required=True)
    parser.add_argument("--catalog-output", type=Path, required=True)
    args = parser.parse_args()

    rows, keys = build_review_rows(
        args.dataset, args.label_audit, args.evidence_audit
    )
    write_csv(args.output, rows)
    write_concept_catalog(args.catalog_output)
    args.key_output.write_text(
        json.dumps(
            {
                "status": "assistant_audited_reference_key_not_for_reviewer",
                "questions": len(keys),
                "items": keys,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"review_rows": len(rows), "key_rows": len(keys)}, indent=2))


if __name__ == "__main__":
    main()
