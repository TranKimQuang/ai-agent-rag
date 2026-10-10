# QASPER query-linking validation v11

Validation v11 được tạo sau khi chọn candidate trên development v10 và được chạy đúng
một lần. Tập gồm 20 paper, 1.157 chunk và 73 câu hỏi; không trùng với 265 paper đã dùng
trước đó. Cấu hình giữ threshold chunk 0,65 và dùng threshold query 0,55 lấy từ bộ nhãn
concept-linking độc lập.

| Phương pháp | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 0,4483 | 0,3420 | 0,3420 |
| Semantic | 0,4463 | 0,3374 | 0,3331 |
| Hybrid | 0,4452 | 0,3283 | 0,3372 |
| Hybrid + Expansion | **0,4566** | 0,3422 | 0,3478 |
| Hybrid + Re-ranking | 0,4452 | 0,3306 | 0,3417 |
| Hybrid + Expansion + Re-ranking | **0,4566** | **0,3438** | **0,3520** |
| Hybrid + Graph exact | 0,4452 | 0,3192 | 0,3304 |

Candidate chính Graph exact không được validation xác nhận: một câu tụt hạng và không có
câu nào cải thiện. Graph không được chọn làm pipeline mặc định.

Query expansion cho tín hiệu tốt trên validation: cứu hai câu vào top-5 và không làm mất
câu nào; cấu hình kết hợp có ba câu cải thiện, hai câu được cứu và một câu xấu đi. Tuy
nhiên, expansion từng giảm điểm tổng trên development v10, nên kết quả hiện là tín hiệu
khả quan nhưng chưa đủ ổn định để đổi pipeline mặc định hoặc mở final-test.

Coverage vẫn thấp: 9/73 query có concept, 31/73 gold evidence có concept và không có cặp
query-gold nào được bộ đo hiện tại xác nhận có quan hệ Ontology trực tiếp. Bước tiếp theo
là đánh giá chất lượng các query links mới và cải thiện concept linking có nhãn, không tăng
trọng số graph hay mở rộng vocabulary thủ công theo validation này.
