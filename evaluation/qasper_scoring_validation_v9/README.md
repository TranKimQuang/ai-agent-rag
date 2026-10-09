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
