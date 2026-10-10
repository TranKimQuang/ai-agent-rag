import argparse
import hashlib
import json
from pathlib import Path

from app.evaluation.qasper import contextualize_split
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original
from scripts.prepare_qasper_result_validation import EXPECTED_SOURCE_SHA256, file_sha256


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a context-enriched copy of an existing QASPER split"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["title", "title_abstract"], required=True)
    parser.add_argument("--abstract-word-limit", type=int, default=80)
    args = parser.parse_args()

    source_hash = file_sha256(args.source)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(f"Unexpected QASPER source SHA-256: {source_hash}")
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install pyarrow to contextualize the QASPER split") from exc

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    selected_ids = set(dataset["metadata"]["paper_ids"])
    papers = {
        paper_id: paper
        for row in pq.read_table(args.source).to_pylist()
        for paper_id, paper in [parquet_row_to_original(row)]
        if paper_id in selected_ids
    }
    if set(papers) != selected_ids:
        missing = sorted(selected_ids - set(papers))
        raise ValueError(f"Source is missing selected papers: {missing}")

    result = contextualize_split(
        dataset,
        papers,
        mode=args.mode,
        abstract_word_limit=args.abstract_word_limit,
    )
    result["metadata"]["base_dataset"] = args.dataset.as_posix()
    content = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(content)
    print(
        json.dumps(
            {
                "output": args.output.as_posix(),
                "mode": args.mode,
                "papers": len(selected_ids),
                "chunks": len(result["chunks"]),
                "questions": len(result["questions"]),
                "sha256": hashlib.sha256(content).hexdigest(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
