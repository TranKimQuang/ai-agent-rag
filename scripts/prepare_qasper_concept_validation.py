from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from rdflib.namespace import SKOS

from app.evaluation.qasper import build_split, select_qasper_papers
from app.evaluation.qasper_protocol import collect_excluded_paper_ids
from app.ontology.service import QA, OntologyService
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original
from scripts.prepare_qasper_result_validation import (
    EXPECTED_SOURCE_SHA256,
    file_sha256,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a sealed, paper-disjoint QASPER concept-linking validation set "
            "and a blinded human-labeling packet"
        )
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--papers", type=int, default=20)
    parser.add_argument("--min-questions-per-paper", type=int, default=3)
    parser.add_argument("--max-questions-per-paper", type=int, default=4)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument(
        "--created-on",
        default=datetime.now(tz=UTC).date().isoformat(),
    )
    return parser.parse_args()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]]) -> bytes:
    if not rows:
        raise ValueError("Cannot write an empty CSV")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path.read_bytes()


def build_blinded_review_rows(dataset: dict[str, object]) -> list[dict[str, str]]:
    chunks = {
        str(chunk["id"]): chunk
        for chunk in dataset["chunks"]  # type: ignore[index]
    }
    rows: list[dict[str, str]] = []
    for number, question in enumerate(dataset["questions"], start=1):  # type: ignore[index]
        evidence = [
            str(chunks[str(chunk_id)]["text"])
            for chunk_id in question["relevant_chunk_ids"]
            if str(chunk_id) in chunks
        ]
        rows.append(
            {
                "review_id": f"CV-{number:03d}",
                "source_question_id": str(question["id"]),
                "paper_id": str(question["paper_id"]),
                "question": str(question["query"]),
                "gold_evidence_excerpt": " || ".join(evidence),
                "reviewer_concepts": "",
                "reviewer_none": "",
                "reviewer_notes": "",
            }
        )
    return rows


def build_concept_catalog_rows() -> list[dict[str, str]]:
    service = OntologyService()
    rows: list[dict[str, str]] = []
    for name in sorted(service.vocabulary_concept_names()):
        concept = QA[name]
        definitions = [
            str(value) for value in service.graph.objects(concept, SKOS.definition)
        ]
        rows.append(
            {
                "concept_id": name,
                "preferred_label": service.preferred_label(concept),
                "definition": " ".join(definitions),
            }
        )
    return rows


def current_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    args = parse_args()
    source_hash = file_sha256(args.input)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"Unexpected QASPER source SHA-256: {source_hash}; "
            f"expected {EXPECTED_SOURCE_SHA256}"
        )
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install pyarrow to prepare the validation set") from exc

    rows = pq.read_table(args.input).to_pylist()
    payload = dict(parquet_row_to_original(row) for row in rows)
    excluded = collect_excluded_paper_ids(args.exclude_dataset)
    papers = select_qasper_papers(
        payload,
        paper_limit=args.papers,
        min_questions_per_paper=args.min_questions_per_paper,
        max_questions_per_paper=args.max_questions_per_paper,
        excluded_paper_ids=excluded,
        selection_seed=args.seed,
    )
    if len(papers) != args.papers:
        raise ValueError(f"Only {len(papers)} eligible QASPER papers were found")

    validation = build_split(
        papers,
        split=f"concept_linking_validation_v{args.version}",
    )
    selected_ids = set(validation["metadata"]["paper_ids"])
    overlap = sorted(selected_ids & excluded)
    if overlap:
        raise ValueError(f"Validation overlaps excluded papers: {overlap}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    validation_path = args.output_dir / "qasper_validation.json"
    validation_content = (
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    validation_path.write_bytes(validation_content)

    review_path = args.output_dir / "blinded_labeling_packet.csv"
    review_content = write_csv(review_path, build_blinded_review_rows(validation))
    catalog_path = args.output_dir / "active_concept_catalog.csv"
    catalog_content = write_csv(catalog_path, build_concept_catalog_rows())

    manifest = {
        "protocol": f"QASPER concept-linking validation v{args.version}",
        "created_on": args.created_on,
        "source": "allenai/qasper qasper/train/0000.parquet",
        "source_sha256": source_hash,
        "selection_seed": args.seed,
        "excluded_dataset_files": [path.as_posix() for path in args.exclude_dataset],
        "excluded_unique_papers": len(excluded),
        "paper_disjoint": True,
        "overlap_with_excluded_papers": overlap,
        "locked_code_commit": current_commit(),
        "validation": {
            "file": validation_path.name,
            "papers": len(validation["metadata"]["paper_ids"]),
            "chunks": len(validation["chunks"]),
            "questions": len(validation["questions"]),
            "sha256": sha256_bytes(validation_content),
            "labeling_packet": review_path.name,
            "labeling_packet_sha256": sha256_bytes(review_content),
            "concept_catalog": catalog_path.name,
            "concept_catalog_sha256": sha256_bytes(catalog_content),
            "label_status": "awaiting_independent_labels",
            "prediction_status": "not_run",
        },
        "policy": (
            "Label the blinded packet before running any linker prediction. Do not tune "
            "on this validation after results are opened. The locked final test remains sealed."
        ),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
