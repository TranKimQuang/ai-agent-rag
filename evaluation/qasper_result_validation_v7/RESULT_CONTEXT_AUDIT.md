# Audit Result extraction trên validation v7

## Phạm vi

- Chạy đúng một lần bộ nhận diện đã khóa tại commit `633724e`.
- Review thủ công toàn bộ 88 instance được tạo trên 20 paper mới.
- Validation v7 paper-disjoint với 185 paper từng dùng; overlap bằng 0.
- Không sửa rule theo kết quả validation này. Final-test v4 vẫn sealed.

## Kết quả

| Hạng mục | Kết quả |
|---|---:|
| Tổng số instance | 88 |
| Result đúng phạm vi | 80 |
| Non-result | 5 |
| Prior-work | 3 |
| Precision instance Result | 90,91% |

| Role | Đúng / tổng | Precision |
|---|---:|---:|
| Method | 15 / 16 | 93,75% |
| Model | 52 / 66 | 78,79% |
| Dataset | 10 / 10 | 100,00% |
| Metric | 88 / 89 | 98,88% |
| Value | 92 / 93 | 98,92% |

## Nhận xét

Precision Result giảm từ 98,28% trên development v6 xuống 90,91% trên paper chưa từng
quan sát, nhưng cao hơn rõ rệt so với 51,72% của validation v5 trước khi sửa. Năm lỗi
non-result còn lại thuộc các đoạn mô tả phương pháp, định nghĩa metric hoặc future work;
ba lỗi prior-work đến từ bài survey/review.

Model role là điểm yếu chính. Mười trong 14 liên kết Model sai đến từ `QA`, vốn là tên
task Question Answering chứ không phải model. Các lỗi còn lại gồm nhãn chung hoặc token
đầu câu như `AI`, `VTE`, `For` và `NER-specific`. Các lỗi này chỉ được ghi nhận cho một
development split tương lai; không sửa bộ nhận diện trên validation v7.

## Artifact

- `result_context_audit_pending.csv`: snapshot duy nhất của lần chạy đã khóa.
- `result_context_review.json`: nhãn review và ghi chú theo instance/role.
- `result_context_audit_summary.json`: precision instance và từng role.
