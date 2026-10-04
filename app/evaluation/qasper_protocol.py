from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.evaluation.qasper import QasperPaperBenchmark, build_split


def collect_excluded_paper_ids(paths: list[Path]) -> set[str]:
    paper_ids: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        paper_ids.update(str(value) for value in payload["metadata"]["paper_ids"])
    return paper_ids


def split_protocol_papers(
    papers: list[QasperPaperBenchmark],
    *,
    development_papers: int,
    validation_papers: int,
    final_test_papers: int,
) -> dict[str, list[QasperPaperBenchmark]]:
    expected = development_papers + validation_papers + final_test_papers
    if min(development_papers, validation_papers, final_test_papers) <= 0:
        raise ValueError("Every protocol split must contain at least one paper")
    if len(papers) != expected:
        raise ValueError(f"Expected {expected} selected papers, received {len(papers)}")
    development_end = development_papers
    validation_end = development_end + validation_papers
    return {
        "development": papers[:development_end],
        "validation": papers[development_end:validation_end],
        "final_test": papers[validation_end:],
    }


def serialize_split(papers: list[QasperPaperBenchmark], *, split: str) -> bytes:
    payload = build_split(papers, split=split)
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
