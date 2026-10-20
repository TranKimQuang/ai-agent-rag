# Đánh giá concept linking theo phân cấp Ontology

Đánh giá này chỉ dùng tập development đã khóa. Chỉ số exact vẫn là chuẩn chính. Chỉ số taxonomy-aware cho 0,5 điểm khi dự đoán và nhãn là quan hệ `skos:broader` cha–con trực tiếp; mỗi concept chỉ được ghép một lần.
Prediction được giới hạn theo cùng catalog nhãn trước khi tính metric.

| Cấu hình | Exact P | Exact R | Exact F1 | Taxonomy P | Taxonomy R | Taxonomy F1 |
|---|---:|---:|---:|---:|---:|---:|
| Whole query | 1.0000 | 0.5882 | 0.7407 | 1.0000 | 0.5882 | 0.7407 |
| Phrase-first | 0.9167 | 0.6471 | 0.7586 | 0.9167 | 0.6471 | 0.7586 |

## Prediction ngoài phạm vi nhãn

- Whole query: 8 assignment.
- Phrase-first: 9 assignment.

## Các trường hợp được ghi nhận là đúng một phần theo taxonomy

Không có trường hợp cha–con trực tiếp trong các dự đoán.

## Kết luận

Không có trường hợp dự đoán–nhãn thuộc quan hệ cha–con trực tiếp, nên taxonomy-aware trùng hoàn toàn với exact. Lần chạy này không cung cấp bằng chứng để triển khai projection cha–con; lỗi còn lại chủ yếu là bỏ sót concept hoặc dự đoán sai concept. Không tuning trên validation/final test.
