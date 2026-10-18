import argparse
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
) -> dict[str, Any]:
    gold_sets = [set(row["gold_concepts"]) for row in rows]
    predictions = [set(row[prediction_field]) for row in rows]
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

    lines.extend(
        [
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
            (
                "Kết quả taxonomy-aware là chỉ số chẩn đoán, không thay thế exact F1. "
                "Nó cho biết một phần sai số đến từ khác biệt mức độ khái quát giữa nhãn "
                "và dự đoán. Không dùng kết quả này để mở hoặc tuning trên "
                "validation/final test."
            ),
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
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    rows = source["rows"]
    service = OntologyService()
    payload = {
        "source_artifact": str(args.input),
        "policy": {
            "exact_credit": 1.0,
            "direct_parent_child_credit": 0.5,
            "transitive_credit": 0.0,
            "matching": "maximum-credit one-to-one",
        },
        "baseline": evaluate_rows(service, rows, "baseline_concepts"),
        "phrase_first": evaluate_rows(service, rows, "phrase_concepts"),
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
