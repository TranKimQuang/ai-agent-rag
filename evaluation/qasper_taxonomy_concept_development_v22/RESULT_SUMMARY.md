# Kết quả taxonomy-focused concept development v22

## Giao thức

- Dữ liệu: 40 câu hỏi QASPER thật thuộc 37 paper, tách khỏi các paper validation,
  final và held-out đã bảo vệ.
- Nhãn được khóa trước prediction: 17 câu dương, 23 câu `NONE`, tổng 17 concept.
- Nguồn nhãn: Qwen3:4b review mù, sau đó assistant audit; đây là nhãn development,
  không phải human gold.
- Cấu hình prediction cố định: threshold 0,65; top-1/top-2 margin 0,03; tối đa 5
  concept. Prediction chỉ được chạy một lần sau khi commit khóa nhãn `85b8de0`.
- Exact Precision/Recall/F1 là chỉ số chính. Taxonomy-aware chỉ là chẩn đoán, cho
  0,5 điểm nếu prediction và gold là cha–con trực tiếp qua `skos:broader`.

## Kết quả trên toàn vocabulary

| Cấu hình | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Whole query | 0,5556 | 0,5882 | 0,5714 | 0,6500 |
| Phrase-first | 0,5238 | 0,6471 | 0,5789 | 0,6250 |

## Kết quả trong phạm vi 22 concept taxonomy được gán nhãn

Để tránh tính prediction ngoài phạm vi nhãn taxonomy là false positive, phép đo thứ hai
lọc prediction theo chính `taxonomy_concept_catalog.csv` trước khi tính metric.

| Cấu hình | Precision | Recall | F1 | Exact match | Prediction bị loại ngoài scope |
|---|---:|---:|---:|---:|---:|
| Whole query | 1,0000 | 0,5882 | 0,7407 | 0,8250 | 8 |
| Phrase-first | 0,9167 | 0,6471 | 0,7586 | 0,8250 | 9 |

Không có prediction–gold nào là quan hệ cha–con trực tiếp. Vì vậy, taxonomy-aware F1
trùng hoàn toàn với exact F1 ở cả hai cấu hình.

## Kết luận kỹ thuật

Kết quả không cung cấp bằng chứng để triển khai projection concept cha–con. Nút thắt
trong tập v22 là bỏ sót cách diễn đạt gián tiếp và một số false positive, không phải
khác biệt mức độ khái quát giữa prediction và gold. Do đó:

1. Không thay đổi Ontology hoặc metric để làm tăng điểm v22.
2. Giữ exact F1 là kết quả chính và giữ taxonomy-aware như chẩn đoán âm.
3. Nếu tiếp tục cải thiện concept linking, chỉ dùng v22 làm development cho recall và
   disambiguation; mọi thay đổi phải được khóa trước một validation mới, độc lập.
4. Không mở hoặc tuning theo validation/final test hiện có.

## Artifact

- `fixed_prediction_once.json`: prediction cố định và metric toàn vocabulary.
- `hierarchical_prediction_once.json` / `HIERARCHICAL_RESULT.md`: đánh giá phân cấp
  trên toàn vocabulary.
- `taxonomy_scoped_hierarchical_result.json` / `TAXONOMY_SCOPED_RESULT.md`: đánh giá
  phân cấp trong phạm vi catalog taxonomy.

