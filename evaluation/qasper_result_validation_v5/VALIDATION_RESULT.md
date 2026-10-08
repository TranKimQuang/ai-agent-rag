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

## Audit extraction độc lập

Đã review toàn bộ 29 Result sau khi khóa cấu hình. Có 15 Result đúng phạm vi và 14 đoạn
non-result, tương ứng precision instance 51,72%. Precision theo role: Method 75,00%,
Model 89,66%, Dataset 86,67%, Metric 100,00% và Value 75,00%.

Kết quả cho thấy scoring có cải thiện retrieval nhưng bộ trích xuất Result chưa khái quát
tốt sang paper mới. Vì vậy chưa chạy final-test v4. Chi tiết và nhãn từng dòng nằm trong
`RESULT_CONTEXT_AUDIT.md`, `result_context_audit.csv`, `result_context_review.json` và
`result_context_audit_summary.json`. Snapshot `result_context_audit_pending.csv` được giữ
nguyên. Không dùng audit này để tuning lại validation v5 hoặc cấu hình đã khóa.
