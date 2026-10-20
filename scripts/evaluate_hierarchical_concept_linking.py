import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.evaluation.hierarchical_concept_linking import score_hierarchical_predictions
from app.ontology.service import OntologyService


def evaluate_rows(
    service: OntologyService,
    rows: list[dict[str, Any]],
    prediction_field: str,
    allowed_concepts: set[str] | None = None,
) -> dict[str, Any]:
    gold_sets = [set(row["gold_concepts"]) for row in rows]
    raw_predictions = [set(row[prediction_field]) for row in rows]
    predictions = [
        prediction & allowed_concepts
        if allowed_concepts is not None
        else prediction
        for prediction in raw_predictions
    ]
    result = score_hierarchical_predictions(service, gold_sets, predictions)
    matches = result.pop("matches")
    changed_rows = []
    for row, row_matches in zip(rows, matches, strict=True):
        taxonomy_matches = [match for match in row_matches if match.credit < 1.0]
        if taxonomy_matches:
            changed_rows.append(
                {
                    "source_question_id": row.get("source_question_id"),
                    "text": row["text"],
                    "gold_concepts": row["gold_concepts"],
                    "predicted_concepts": row[prediction_field],
                    "taxonomy_matches": [asdict(match) for match in taxonomy_matches],
                }
            )
    result["taxonomy_matched_rows"] = changed_rows
    result["excluded_prediction_assignments"] = sum(
        len(raw - filtered)
        for raw, filtered in zip(raw_predictions, predictions, strict=True)
    )
    return result


def write_report(payload: dict[str, Any], path: Path) -> None:
    baseline = payload["baseline"]
    phrase = payload["phrase_first"]
    lines = [
        "# Đánh giá concept linking theo phân cấp Ontology",
        "",
        (
            "Đánh giá này chỉ dùng tập development đã khóa. Chỉ số exact vẫn là chuẩn chính. "
            "Chỉ số taxonomy-aware cho 0,5 điểm khi dự đoán và nhãn là quan hệ "
            "`skos:broader` cha–con trực tiếp; mỗi concept chỉ được ghép một lần."
        ),
        (
            "Prediction được giới hạn theo cùng catalog nhãn trước khi tính metric."
            if isinstance(payload["concept_scope"], dict)
            else "Prediction được đánh giá trên toàn bộ vocabulary."
        ),
        "",
        "| Cấu hình | Exact P | Exact R | Exact F1 | Taxonomy P | Taxonomy R | Taxonomy F1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in (("Whole query", baseline), ("Phrase-first", phrase)):
        exact = result["exact"]
        taxonomy = result["taxonomy_aware"]
        lines.append(
            f"| {name} | {exact['precision']:.4f} | {exact['recall']:.4f} | "
            f"{exact['f1']:.4f} | {taxonomy['precision']:.4f} | "
            f"{taxonomy['recall']:.4f} | {taxonomy['f1']:.4f} |"
        )

    has_partial_matches = any(
        result["taxonomy_matched_rows"] for result in (baseline, phrase)
    )
    conclusion = (
        "Kết quả taxonomy-aware là chỉ số chẩn đoán, không thay thế exact F1. "
        "Các trường hợp đúng một phần cho thấy một phần sai số đến từ khác biệt mức độ "
        "khái quát giữa nhãn và dự đoán. Không dùng kết quả này để mở hoặc tuning trên "
        "validation/final test."
        if has_partial_matches
        else
        "Không có trường hợp dự đoán–nhãn thuộc quan hệ cha–con trực tiếp, nên "
        "taxonomy-aware trùng hoàn toàn với exact. Lần chạy này không cung cấp bằng "
        "chứng để triển khai projection cha–con; lỗi còn lại chủ yếu là bỏ sót concept "
        "hoặc dự đoán sai concept. Không tuning trên validation/final test."
    )
    lines.extend(
        [
            "",
            "## Prediction ngoài phạm vi nhãn",
            "",
            f"- Whole query: {baseline['excluded_prediction_assignments']} assignment.",
            f"- Phrase-first: {phrase['excluded_prediction_assignments']} assignment.",
            "",
            "## Các trường hợp được ghi nhận là đúng một phần theo taxonomy",
            "",
        ]
    )
    unique_rows = {
        (row["source_question_id"], match["predicted"], match["gold"]): (row, match)
        for result in (baseline, phrase)
        for row in result["taxonomy_matched_rows"]
        for match in row["taxonomy_matches"]
    }
    if not unique_rows:
        lines.append("Không có trường hợp cha–con trực tiếp trong các dự đoán.")
    else:
        for row, match in unique_rows.values():
            lines.append(
                f"- `{match['predicted']}` ↔ `{match['gold']}` "
                f"({match['relation']}, 0,5 điểm): {row['text']}"
            )

    lines.extend(
        [
            "",
            "## Kết luận",
            "",
            conclusion,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-score saved concept-linking predictions with SKOS hierarchy"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--concept-catalog",
        type=Path,
        help="Optionally restrict predictions to the same labelled concept scope.",
    )
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    rows = source["rows"]
    service = OntologyService()
    allowed_concepts = None
    if args.concept_catalog:
        with args.concept_catalog.open(encoding="utf-8-sig", newline="") as handle:
            allowed_concepts = {
                row["concept_id"].strip() for row in csv.DictReader(handle)
            }
    payload = {
        "source_artifact": str(args.input),
        "concept_scope": (
            {
                "catalog": str(args.concept_catalog),
                "allowed_concepts": sorted(allowed_concepts),
            }
            if allowed_concepts is not None
            else "all prediction concepts"
        ),
        "policy": {
            "exact_credit": 1.0,
            "direct_parent_child_credit": 0.5,
            "transitive_credit": 0.0,
            "matching": "maximum-credit one-to-one",
        },
        "baseline": evaluate_rows(
            service, rows, "baseline_concepts", allowed_concepts
        ),
        "phrase_first": evaluate_rows(
            service, rows, "phrase_concepts", allowed_concepts
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_report(payload, args.report)
    print(
        json.dumps(
            {
                name: {
                    "exact": payload[name]["exact"],
                    "taxonomy_aware": payload[name]["taxonomy_aware"],
                    "taxonomy_matched_rows": len(payload[name]["taxonomy_matched_rows"]),
                }
                for name in ("baseline", "phrase_first")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
