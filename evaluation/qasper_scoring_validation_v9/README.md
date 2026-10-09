# QASPER context-aware Ontology scoring validation v9

Validation v9 kiểm tra đúng một lần candidate context gate đã chọn trên development v8.

- 20 paper, 1.391 chunk và 78 câu hỏi có gold evidence.
- Loại 225 paper đã dùng trong toàn bộ split trước, bao gồm development v8.
- Overlap với các paper bị loại bằng 0.
- Candidate code: commit `4d5403a`.
- Selection record: commit `30e94f0`.
- Hash dataset: `9afe6cd1178a02c3a78b286407d6e2f63feedb9364a2141e1e7bb5a305d21231`.

Không thay đổi rule, threshold hoặc weight sau khi xem kết quả v9. Final-test v4 tiếp tục
được niêm phong.

## Kết quả lần chạy duy nhất

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,2928 | 0,2472 | 0,2343 |
| Hybrid + Expansion | 0,2928 | 0,2408 | 0,2296 |
| Hybrid + context-gated Re-ranking | 0,2928 | 0,2472 | 0,2343 |
| Hybrid + Expansion + Re-ranking | 0,2928 | 0,2408 | 0,2296 |

Context-gated re-ranking giữ nguyên thứ hạng của cả 78/78 câu: không cải thiện, không
làm xấu và không làm mất câu nào khỏi top-5. Coverage giải thích kết quả này: chỉ 1/78
query có concept, 28/78 gold evidence có concept và chỉ 1/78 cặp query-gold có quan hệ
Ontology. Kết luận: context gate khái quát được khả năng tránh gây hại, nhưng concept
linking/vocabulary hiện chưa khái quát đủ để tạo lợi ích trên paper mới.

Không tuning lại trên v9.
