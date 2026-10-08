# Kết quả validation v5 cho Result-context scoring

## Protocol

- Ngày chạy: 08/10/2026.
- 20 paper, 1.109 chunk, 75 câu hỏi QASPER có gold evidence.
- Không trùng 145 paper đã xuất hiện trong các protocol trước.
- Chạy đúng một sweep đã định trước với weight `0`, `0.05`, `0.10`, `0.20`, `0.30`.
- Final-test v4 không được mở hoặc đánh giá.

## Kết quả chính

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,2333 | 0,1693 | 0,1699 |
| Query Expansion | 0,2200 | 0,1649 | 0,1623 |
| Ontology re-ranking, weight 0,20 | **0,2533** | **0,1804** | **0,1848** |

So với Hybrid, Ontology re-ranking tăng Recall@5 thêm 0,0200, MRR@5 thêm 0,0111
và nDCG@5 thêm 0,0149. Có 3 câu tăng hạng, 2 câu được cứu vào top 5, 2 câu giảm
hạng và không có câu nào bị mất khỏi top 5.

Query expansion tiếp tục giảm cả ba chỉ số, nên bị tắt trong cấu hình khóa.

## Lựa chọn weight

Weight `0,20` có nDCG@5 cao nhất (`0,1847966`) theo quy tắc lựa chọn đã khai báo.
Weight `0,10` rất gần (`0,1846387`) và có MRR@5 cao hơn nhẹ, nhưng không được chọn vì
nDCG@5 là chỉ số ưu tiên thứ nhất. Không điều chỉnh quy tắc sau khi xem kết quả.

Cấu hình được lưu tại `locked_result_context_config.json`. Validation v5 không được dùng
cho vòng tuning tiếp theo; nếu thay đổi thuật toán phải tạo một paper-disjoint split mới.

## Bước kiểm tra còn lại

Đã xuất 29 Result của validation vào `result_context_audit_pending.csv`. Cần review độc lập
để đo precision extraction trên paper mới. Việc review này không được dùng để sửa cấu hình
đã khóa trước khi chạy final-test hiện tại.
