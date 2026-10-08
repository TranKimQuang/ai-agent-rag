# QASPER Result-context validation v5

Validation này được tạo từ QASPER train chính thức để kiểm tra khả năng khái quát của
Result-centric Ontology scoring sau khi audit development.

- 20 paper, 1.109 chunk và 75 câu hỏi có gold evidence.
- Loại 145 paper đã xuất hiện trong chín dataset development/validation/held-out trước đó.
- Không trùng bất kỳ paper bị loại nào.
- Seed chọn paper: `20261007`.
- Trạng thái: `prepared_not_evaluated`.
- QASPER final-test v4 vẫn giữ `sealed_not_evaluated`.

Trước khi chạy validation này, cần giữ nguyên bộ lọc Result hiện tại và tập weight đã định
trước (`0`, `0.05`, `0.10`, `0.20`, `0.30`). Sau khi xem kết quả, không tiếp tục sửa cấu
hình trên cùng split; nếu cần một vòng phát triển mới thì phải tạo paper split khác.

Chi tiết hash nguồn, hash split và danh sách file bị loại nằm trong `manifest.json`.
