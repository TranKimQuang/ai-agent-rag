from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from app.evaluation.qasper import build_split, select_qasper_papers
from app.evaluation.qasper_protocol import collect_excluded_paper_ids
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original

EXPECTED_SOURCE_SHA256 = "9af08092ee26c4f700202c1f90d1592b662926f23f3a308a10ff0a53345e37fe"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare an independent QASPER validation for Result scoring"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluation/qasper_result_validation_v5"),
    )
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--papers", type=int, default=20)
    parser.add_argument("--min-questions-per-paper", type=int, default=3)
    parser.add_argument("--max-questions-per-paper", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261007)
    return parser.parse_args()


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
        raise RuntimeError("Install pyarrow to prepare the QASPER validation") from exc

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

    validation = build_split(papers, split="result_context_validation_v5")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    validation_path = args.output_dir / "qasper_validation.json"
    validation_content = (
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    validation_path.write_bytes(validation_content)

    selected_ids = set(validation["metadata"]["paper_ids"])
    overlap = sorted(selected_ids & excluded)
    if overlap:
        raise ValueError(f"Validation overlaps excluded papers: {overlap}")
    manifest = {
        "protocol": "QASPER Result-context validation v5",
        "created_on": "2026-10-07",
        "source": "allenai/qasper qasper/train/0000.parquet",
        "source_sha256": source_hash,
        "selection_seed": args.seed,
        "excluded_dataset_files": [path.as_posix() for path in args.exclude_dataset],
        "excluded_unique_papers": len(excluded),
        "paper_disjoint": True,
        "overlap_with_excluded_papers": overlap,
        "validation": {
            "file": validation_path.name,
            "papers": len(validation["metadata"]["paper_ids"]),
            "chunks": len(validation["chunks"]),
            "questions": len(validation["questions"]),
            "sha256": hashlib.sha256(validation_content).hexdigest(),
            "evaluation_status": "prepared_not_evaluated",
        },
        "policy": (
            "Do not alter Result extraction rules or ontology weight after observing this "
            "validation without creating another paper-disjoint split. Final-test v4 remains "
            "sealed."
        ),
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
