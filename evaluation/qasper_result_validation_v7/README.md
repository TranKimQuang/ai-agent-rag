# QASPER Result-extraction validation v7

Validation v7 dùng để kiểm tra khả năng khái quát của bộ nhận diện `Result` đã sửa và
khóa tại commit `633724e`.

- 20 paper, 1.314 chunk và 76 câu hỏi có gold evidence.
- Loại 185 paper đã xuất hiện trong toàn bộ split cũ, gồm development v6 và validation v5.
- Overlap với tập bị loại bằng 0.
- Seed chọn paper: `20261009`.
- Trạng thái: `evaluated_once`.
- Hash dataset: `f20637a577fdbbf7d6399172323f5339bd6675fed07478d03f3a40e3d716e61a`.

Quy tắc đánh giá:

1. Commit dataset, manifest và cấu hình khóa trước khi chạy.
2. Chạy Result extraction đúng một lần trên validation v7.
3. Review toàn bộ instance được tạo nhưng không sửa rule theo kết quả validation này.
4. Nếu kết quả không đạt, quay lại một development split mới; không tuning trên v7.
5. Final-test v4 tiếp tục được niêm phong.

Chi tiết nguồn dữ liệu, danh sách file bị loại và chính sách nằm trong `manifest.json`;
cấu hình khóa nằm trong `locked_result_extraction_config.json`.

Lần chạy duy nhất tạo 88 instance. Review xác nhận 80 Result đúng phạm vi, 5 non-result
và 3 prior-work; precision instance đạt 90,91%. Xem `RESULT_CONTEXT_AUDIT.md` và
`result_context_audit_summary.json` để biết chi tiết. Không tuning lại trên v7.

## Retrieval khóa cấu hình

Cấu hình được commit trước khi chạy: Hybrid concept linking threshold 0,65,
Ontology weight 0,20, không dùng query expansion cho cấu hình chính. Benchmark ablation
được chạy đúng một lần trên 76 câu hỏi.

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,2823 | 0,2318 | 0,2307 |
| Hybrid + Expansion | 0,2692 | 0,2186 | 0,2176 |
| Hybrid + Re-ranking | 0,2692 | 0,2208 | 0,2190 |
| Hybrid + Expansion + Re-ranking | 0,2560 | 0,2175 | 0,2133 |

Re-ranking cải thiện thứ hạng của 3 câu, làm xấu 3 câu, giữ nguyên 69 câu và làm mất
1 câu khỏi top-5. Kết quả không xác nhận cải thiện trung bình so với Hybrid; nDCG@5 giảm
0,0117. Không điều chỉnh trọng số hoặc rule theo v7. Chi tiết từng câu nằm trong
`locked_retrieval_once.json`.
