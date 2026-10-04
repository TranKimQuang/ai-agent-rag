from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.qasper import select_qasper_papers
from app.evaluation.qasper_protocol import (
    collect_excluded_paper_ids,
    serialize_split,
    sha256_bytes,
    split_protocol_papers,
)
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
        description="Create a paper-disjoint QASPER protocol with a sealed final test."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("evaluation/qasper_protocol_v4")
    )
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    parser.add_argument("--development-papers", type=int, default=20)
    parser.add_argument("--validation-papers", type=int, default=10)
    parser.add_argument("--final-test-papers", type=int, default=15)
    parser.add_argument("--min-questions-per-paper", type=int, default=3)
    parser.add_argument("--max-questions-per-paper", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20261003)
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
        raise RuntimeError("Install pyarrow to prepare the QASPER protocol") from exc

    rows = pq.read_table(args.input).to_pylist()
    payload = dict(parquet_row_to_original(row) for row in rows)
    excluded = collect_excluded_paper_ids(args.exclude_dataset)
    total_papers = (
        args.development_papers + args.validation_papers + args.final_test_papers
    )
    papers = select_qasper_papers(
        payload,
        paper_limit=total_papers,
        min_questions_per_paper=args.min_questions_per_paper,
        max_questions_per_paper=args.max_questions_per_paper,
        excluded_paper_ids=excluded,
        selection_seed=args.seed,
    )
    if len(papers) != total_papers:
        raise ValueError(f"Only {len(papers)} eligible QASPER papers were found")
    splits = split_protocol_papers(
        papers,
        development_papers=args.development_papers,
        validation_papers=args.validation_papers,
        final_test_papers=args.final_test_papers,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_splits: dict[str, object] = {}
    for name, selected in splits.items():
        filename = f"qasper_{name}.json"
        content = serialize_split(selected, split=f"protocol_v4_{name}")
        path = args.output_dir / filename
        path.write_bytes(content)
        payload_count = json.loads(content)
        manifest_splits[name] = {
            "file": filename,
            "papers": len(selected),
            "chunks": len(payload_count["chunks"]),
            "questions": len(payload_count["questions"]),
            "sha256": sha256_bytes(content),
            "evaluation_status": (
                "sealed_not_evaluated" if name == "final_test" else "available"
            ),
        }

    manifest = {
        "protocol": "QASPER protocol v4",
        "created_on": "2026-10-03",
        "source": "allenai/qasper qasper/train/0000.parquet",
        "source_sha256": source_hash,
        "selection_seed": args.seed,
        "excluded_dataset_files": [path.as_posix() for path in args.exclude_dataset],
        "excluded_unique_papers": len(excluded),
        "paper_disjoint": True,
        "final_test_policy": (
            "Do not inspect retrieval results or tune on final_test. Freeze and commit the "
            "configuration before one-time evaluation."
        ),
        "splits": manifest_splits,
    }
    manifest_path = args.output_dir / "protocol_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    readme = args.output_dir / "README.md"
    readme.write_text(
        "# QASPER protocol v4\n\n"
        "This protocol excludes every paper used by the earlier QASPER protocols. "
        "Paper selection is deterministic and paper-disjoint.\n\n"
        "- Development may be used for error analysis and method development.\n"
        "- Validation may be used for selecting thresholds and configurations.\n"
        "- Final test is sealed and has not been evaluated. Commit the frozen "
        "configuration before running it once.\n\n"
        "See `protocol_manifest.json` for counts, SHA-256 hashes and the selection seed.\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
