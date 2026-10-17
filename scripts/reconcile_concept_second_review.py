import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_reviewer_labels(row: dict[str, str], active: set[str]) -> set[str]:
    labels = {
        value.strip()
        for value in row.get("reviewer_concepts", "").split(";")
        if value.strip()
    }
    marked_none = row.get("reviewer_none", "").strip().lower() in {
        "x",
        "yes",
        "true",
        "1",
    }
    if bool(labels) == marked_none:
        raise ValueError(
            f'{row.get("review_id", "unknown")}: fill concepts or reviewer_none, not both/neither'
        )
    unknown = sorted(labels - active)
    if unknown:
        raise ValueError(
            f'{row.get("review_id", "unknown")}: unknown concepts {unknown}'
        )
    return labels


def reconcile(
    review_rows: list[dict[str, str]],
    reference_items: list[dict[str, Any]],
    active: set[str],
) -> dict[str, Any]:
    reference = {str(item["review_id"]): item for item in reference_items}
    if len(reference) != len(reference_items):
        raise ValueError("Duplicate review IDs in reference key")
    seen: set[str] = set()
    exact = 0
    positive_agreement = 0
    label_true_positive = 0
    reviewer_label_total = 0
    reference_label_total = 0
    disagreements = []
    for row in review_rows:
        review_id = row.get("review_id", "")
        if review_id in seen:
            raise ValueError(f"Duplicate review ID: {review_id}")
        seen.add(review_id)
        if review_id not in reference:
            raise ValueError(f"Review ID absent from reference key: {review_id}")
        reviewer = parse_reviewer_labels(row, active)
        expected = set(reference[review_id]["audited_concepts"])
        exact += int(reviewer == expected)
        positive_agreement += int(bool(reviewer) == bool(expected))
        label_true_positive += len(reviewer & expected)
        reviewer_label_total += len(reviewer)
        reference_label_total += len(expected)
        if reviewer != expected:
            disagreements.append(
                {
                    "review_id": review_id,
                    "source_question_id": reference[review_id]["source_question_id"],
                    "paper_id": row.get("paper_id", ""),
                    "question": row.get("question", ""),
                    "gold_evidence_excerpt": row.get("gold_evidence_excerpt", ""),
                    "assistant_audited_concepts": sorted(expected),
                    "second_reviewer_concepts": sorted(reviewer),
                    "reviewer_notes": row.get("reviewer_notes", ""),
                }
            )
    missing = sorted(set(reference) - seen)
    if missing:
        raise ValueError(f"Reference rows missing from completed review: {missing}")
    precision = (
        label_true_positive / reviewer_label_total if reviewer_label_total else 0.0
    )
    recall = (
        label_true_positive / reference_label_total if reference_label_total else 0.0
    )
    return {
        "status": "requires_disagreement_resolution"
        if disagreements
        else "independent_review_agreed",
        "questions": len(review_rows),
        "exact_agreement": exact / len(review_rows) if review_rows else 0.0,
        "positive_negative_agreement": (
            positive_agreement / len(review_rows) if review_rows else 0.0
        ),
        "label_precision_against_assistant_audit": precision,
        "label_recall_against_assistant_audit": recall,
        "label_f1_against_assistant_audit": (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        ),
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcile independent concept labels")
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--reference-key", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--disagreement-csv", type=Path)
    args = parser.parse_args()

    with args.review.open(encoding="utf-8-sig", newline="") as handle:
        review_rows = list(csv.DictReader(handle))
    with args.catalog.open(encoding="utf-8-sig", newline="") as handle:
        active = {row["concept_id"] for row in csv.DictReader(handle)}
    reference_payload = json.loads(args.reference_key.read_text(encoding="utf-8"))
    result = reconcile(review_rows, reference_payload["items"], active)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.disagreement_csv:
        args.disagreement_csv.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "review_id",
            "source_question_id",
            "paper_id",
            "question",
            "gold_evidence_excerpt",
            "assistant_audited_concepts",
            "second_reviewer_concepts",
            "reviewer_notes",
            "adjudicated_concepts",
            "adjudication_notes",
        ]
        with args.disagreement_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for disagreement in result["disagreements"]:
                writer.writerow(
                    {
                        **disagreement,
                        "assistant_audited_concepts": ";".join(
                            disagreement["assistant_audited_concepts"]
                        ),
                        "second_reviewer_concepts": ";".join(
                            disagreement["second_reviewer_concepts"]
                        ),
                        "adjudicated_concepts": "",
                        "adjudication_notes": "",
                    }
                )
    print(json.dumps({key: value for key, value in result.items() if key != "disagreements"}, indent=2))


if __name__ == "__main__":
    main()
