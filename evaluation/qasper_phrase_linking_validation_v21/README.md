# QASPER phrase-linking validation v21

## Protocol khóa trước prediction

- 30 paper, 1.833 chunk, 49 câu hỏi có gold evidence.
- Không trùng với 405 paper đã dùng trước v21.
- Candidate đã khóa tại commit `a798729`: phrase-first Hybrid, threshold 0,65,
  Top-1/Top-2 margin 0,03, limit 5.
- Reviewer độc lập gán đủ 49 câu: 17 dương, 32 `NONE`, 20 concept assignment.
- Prediction chưa chạy tại thời điểm khóa nhãn.
- Không tuning trên v19 hoặc v21; final test vẫn niêm phong.

Sau khi commit nhãn, candidate được chạy đúng một lần bằng
`scripts.evaluate_phrase_query_linking`. Không quét threshold/margin trên v21.

