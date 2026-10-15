# Document-topic prior validation v16

## Trạng thái trước đánh giá

- 20 QASPER paper, 1.494 chunk, 77 câu hỏi có gold evidence.
- Không trùng với 305 paper trong các development/validation/final-test trước.
- Dataset SHA-256: `8e172b89c3d64de265bce247b97f0e12405766b489acbf4a4f9e3c4e208dc5eb`.
- Candidate code: commit `38ccd4e`.
- Candidate được chọn duy nhất từ development v15.

## Candidate đã khóa

So sánh chính là Hybrid với Hybrid + Ontology re-ranking. Query dùng phrase-first
semantic linking; prior lấy concept từ toàn bộ bài báo nguồn, cộng 0,05 cho semantic
candidate được hồ sơ bài báo hỗ trợ và trừ 0,05 cho candidate không được hỗ trợ.

Không dùng document-topic prior cho query expansion. Exact alias không bị điều chỉnh.
Sau khi chạy, không thay threshold/trọng số theo validation này và không mở final-test v4.
