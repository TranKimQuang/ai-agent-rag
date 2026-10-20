# Đánh giá concept linking theo phân cấp Ontology

Đánh giá này chỉ dùng tập development đã khóa. Chỉ số exact vẫn là chuẩn chính. Chỉ số taxonomy-aware cho 0,5 điểm khi dự đoán và nhãn là quan hệ `skos:broader` cha–con trực tiếp; mỗi concept chỉ được ghép một lần.
Prediction được đánh giá trên toàn bộ vocabulary.

| Cấu hình | Exact P | Exact R | Exact F1 | Taxonomy P | Taxonomy R | Taxonomy F1 |
|---|---:|---:|---:|---:|---:|---:|
| Whole query | 0.5556 | 0.5882 | 0.5714 | 0.5556 | 0.5882 | 0.5714 |
| Phrase-first | 0.5238 | 0.6471 | 0.5789 | 0.5238 | 0.6471 | 0.5789 |

## Prediction ngoài phạm vi nhãn

- Whole query: 0 assignment.
- Phrase-first: 0 assignment.

## Các trường hợp được ghi nhận là đúng một phần theo taxonomy

Không có trường hợp cha–con trực tiếp trong các dự đoán.

## Kết luận

Không có trường hợp dự đoán–nhãn thuộc quan hệ cha–con trực tiếp, nên taxonomy-aware trùng hoàn toàn với exact. Lần chạy này không cung cấp bằng chứng để triển khai projection cha–con; lỗi còn lại chủ yếu là bỏ sót concept hoặc dự đoán sai concept. Không tuning trên validation/final test.
