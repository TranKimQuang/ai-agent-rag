# Đánh giá concept linking theo phân cấp Ontology

Đánh giá này chỉ dùng tập development đã khóa. Chỉ số exact vẫn là chuẩn chính. Chỉ số taxonomy-aware cho 0,5 điểm khi dự đoán và nhãn là quan hệ `skos:broader` cha–con trực tiếp; mỗi concept chỉ được ghép một lần.

| Cấu hình | Exact P | Exact R | Exact F1 | Taxonomy P | Taxonomy R | Taxonomy F1 |
|---|---:|---:|---:|---:|---:|---:|
| Whole query | 0.8571 | 0.3529 | 0.5000 | 0.9286 | 0.3824 | 0.5417 |
| Phrase-first | 0.7500 | 0.4412 | 0.5556 | 0.8000 | 0.4706 | 0.5926 |

## Các trường hợp được ghi nhận là đúng một phần theo taxonomy

- `SemanticRoleInduction` ↔ `NaturalLanguageProcessing` (predicted_is_narrower, 0,5 điểm): Are there syntax-agnostic SRL models before?
- `MachineReadingComprehension` ↔ `QuestionAnswering` (predicted_is_narrower, 0,5 điểm): How much performance improvements they achieve on SQuAD?

## Kết luận

Kết quả taxonomy-aware là chỉ số chẩn đoán, không thay thế exact F1. Nó cho biết một phần sai số đến từ khác biệt mức độ khái quát giữa nhãn và dự đoán. Không dùng kết quả này để mở hoặc tuning trên validation/final test.
