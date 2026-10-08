# QASPER Result-context validation v5

Validation này được tạo từ QASPER train chính thức để kiểm tra khả năng khái quát của
Result-centric Ontology scoring sau khi audit development.

- 20 paper, 1.109 chunk và 75 câu hỏi có gold evidence.
- Loại 145 paper đã xuất hiện trong chín dataset development/validation/held-out trước đó.
- Không trùng bất kỳ paper bị loại nào.
- Seed chọn paper: `20261007`.
- Trạng thái: `evaluated_once` ngày 08/10/2026.
- QASPER final-test v4 vẫn giữ `sealed_not_evaluated`.

Validation đã chạy đúng một sweep với các weight định trước (`0`, `0.05`, `0.10`, `0.20`,
`0.30`). Weight `0,20` được chọn theo nDCG@5 và cấu hình đã được khóa. Không tiếp tục sửa
cấu hình trên cùng split; nếu cần một vòng phát triển mới thì phải tạo paper split khác.

Chi tiết hash nguồn, hash split và danh sách file bị loại nằm trong `manifest.json`.
