from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from app.evaluation.qasper import build_split, select_qasper_papers
from app.evaluation.qasper_protocol import collect_excluded_paper_ids
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original
from scripts.prepare_qasper_result_validation import (
    EXPECTED_SOURCE_SHA256,
    file_sha256,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a paper-disjoint QASPER development split for Result extraction"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluation/qasper_result_development_v6"),
    )
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--papers", type=int, default=20)
    parser.add_argument("--min-questions-per-paper", type=int, default=3)
    parser.add_argument("--max-questions-per-paper", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261008)
    parser.add_argument(
        "--created-on",
        default=datetime.now(tz=UTC).date().isoformat(),
    )
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
        raise RuntimeError("Install pyarrow to prepare the QASPER development split") from exc

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

    development = build_split(papers, split="result_context_development_v6")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    development_path = args.output_dir / "qasper_development.json"
    development_content = (
        json.dumps(development, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    development_path.write_bytes(development_content)

    selected_ids = set(development["metadata"]["paper_ids"])
    overlap = sorted(selected_ids & excluded)
    if overlap:
        raise ValueError(f"Development split overlaps excluded papers: {overlap}")

    manifest = {
        "protocol": "QASPER Result-extraction development v6",
        "created_on": args.created_on,
        "source": "allenai/qasper qasper/train/0000.parquet",
        "source_sha256": source_hash,
        "selection_seed": args.seed,
        "excluded_dataset_files": [path.as_posix() for path in args.exclude_dataset],
        "excluded_unique_papers": len(excluded),
        "paper_disjoint": True,
        "overlap_with_excluded_papers": overlap,
        "development": {
            "file": development_path.name,
            "papers": len(development["metadata"]["paper_ids"]),
            "chunks": len(development["chunks"]),
            "questions": len(development["questions"]),
            "sha256": hashlib.sha256(development_content).hexdigest(),
            "status": "prepared_not_reviewed",
        },
        "policy": (
            "This split may be used to improve Result extraction. Do not tune on "
            "validation v5 or sealed final-test v4. Evaluate changes on a new "
            "paper-disjoint validation split."
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
