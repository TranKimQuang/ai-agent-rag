# QASPER Result-extraction development v6

Development split này dùng để cải thiện khả năng nhận diện `Result` sau khi validation v5
cho thấy precision instance chỉ đạt 51,72% trên paper mới.

- 20 paper, 1.044 chunk và 69 câu hỏi có gold evidence.
- Loại 165 paper từng xuất hiện trong toàn bộ split cũ, bao gồm cả validation v5.
- Overlap với tập bị loại bằng 0.
- Seed chọn paper: `20261008`.
- Trạng thái: `reviewed_baseline`.
- Bộ trích xuất hiện tại tạo 44 instance trong `result_context_audit_pending.csv`.
- Audit baseline: 30 Result đúng phạm vi, 7 non-result và 7 prior-work; precision instance
  68,18%. Dataset role thấp nhất với precision 56,25%.

Split này được phép dùng để review và sửa thuật toán. Không dùng lại validation v5 để
tuning và không mở final-test v4. Sau khi khóa thay đổi, phải tạo một validation mới khác,
paper-disjoint với cả development v6, để đánh giá đúng một lần.

Chi tiết hash nguồn, hash dataset, danh sách file bị loại và chính sách sử dụng nằm trong
`manifest.json`.
