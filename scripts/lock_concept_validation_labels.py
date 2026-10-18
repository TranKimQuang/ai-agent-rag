from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_concepts(raw: str) -> list[str]:
    return sorted({value.strip() for value in raw.split("|") if value.strip()})


def build_locked_labels(
    packet_rows: list[dict[str, str]],
    label_rows: list[dict[str, str]],
    valid_concepts: set[str],
) -> tuple[list[dict[str, object]], dict[str, int]]:
    labels_by_id: dict[str, dict[str, str]] = {}
    for row in label_rows:
        review_id = row.get("review_id", "").strip()
        if not review_id or review_id in labels_by_id:
            raise ValueError(f"Missing or duplicate review_id: {review_id!r}")
        labels_by_id[review_id] = row

    packet_ids = {row["review_id"] for row in packet_rows}
    if set(labels_by_id) != packet_ids:
        missing = sorted(packet_ids - set(labels_by_id))
        extra = sorted(set(labels_by_id) - packet_ids)
        raise ValueError(f"Label/packet mismatch; missing={missing}, extra={extra}")

    locked: list[dict[str, object]] = []
    positive = 0
    assignments = 0
    for packet in packet_rows:
        review_id = packet["review_id"]
        review = labels_by_id[review_id]
        concepts = parse_concepts(review.get("reviewer_concepts", ""))
        none_value = review.get("reviewer_none", "").strip().lower()
        is_none = none_value in {"1", "true", "yes", "x"}
        if bool(concepts) == is_none:
            raise ValueError(
                f"{review_id} must have exactly one of concepts or reviewer_none=1"
            )
        unknown = sorted(set(concepts) - valid_concepts)
        if unknown:
            raise ValueError(f"{review_id} contains unknown concepts: {unknown}")
        positive += int(bool(concepts))
        assignments += len(concepts)
        locked.append(
            {
                "source_question_id": packet["source_question_id"],
                "text": packet["question"],
                "gold_concepts": concepts,
                "review_id": review_id,
            }
        )

    return locked, {
        "questions": len(locked),
        "positive_questions": positive,
        "none_questions": len(locked) - positive,
        "concept_assignments": assignments,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and lock independent concept-linking labels"
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--section",
        choices=("development", "validation"),
        default="validation",
        help="Manifest section to update.",
    )
    args = parser.parse_args()

    packet_rows = read_csv(args.packet)
    label_rows = read_csv(args.labels)
    catalog_rows = read_csv(args.catalog)
    valid_concepts = {row["concept_id"].strip() for row in catalog_rows}
    locked, summary = build_locked_labels(packet_rows, label_rows, valid_concepts)

    args.output.write_text(
        json.dumps(locked, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    target = manifest[args.section]
    if target.get("prediction_status") != "not_run":
        raise ValueError(
            f"Cannot relock labels after {args.section} prediction was run"
        )
    target.update(
        {
            "label_status": "independent_labels_locked_before_prediction",
            "independent_labels": args.labels.name,
            "independent_labels_sha256": file_sha256(args.labels),
            "locked_labels": args.output.name,
            "locked_labels_sha256": file_sha256(args.output),
            "label_summary": summary,
        }
    )
    args.manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
