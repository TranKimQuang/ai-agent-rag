# QASPER Result-extraction development v6

Development split này dùng để cải thiện khả năng nhận diện `Result` sau khi validation v5
cho thấy precision instance chỉ đạt 51,72% trên paper mới.

- 20 paper, 1.044 chunk và 69 câu hỏi có gold evidence.
- Loại 165 paper từng xuất hiện trong toàn bộ split cũ, bao gồm cả validation v5.
- Overlap với tập bị loại bằng 0.
- Seed chọn paper: `20261008`.
- Trạng thái: `post_fix_reviewed`.
- Bộ trích xuất hiện tại tạo 44 instance trong `result_context_audit_pending.csv`.
- Audit baseline: 30 Result đúng phạm vi, 7 non-result và 7 prior-work; precision instance
  68,18%. Dataset role thấp nhất với precision 56,25%.
- Sau sửa, bộ trích xuất tạo 58 instance: giữ đủ 30/30 Result đúng đã biết, loại đủ
  14/14 instance sai đã biết và tìm thêm 28 ứng viên. Review toàn bộ nhóm mới xác nhận
  57/58 instance đúng phạm vi, precision development 98,28%.
- Precision role hậu sửa: Method 100%, Model 98,25%, Dataset 77,78%, Metric 100%
  và Value 100%.

Split này được phép dùng để review và sửa thuật toán. Không dùng lại validation v5 để
tuning và không mở final-test v4. Sau khi khóa thay đổi, phải tạo một validation mới khác,
paper-disjoint với cả development v6, để đánh giá đúng một lần.

Chi tiết hash nguồn, hash dataset, danh sách file bị loại và chính sách sử dụng nằm trong
`manifest.json`.

Nhãn hậu sửa nằm trong `result_context_review_after_fix.json`; số liệu tổng hợp nằm trong
`result_context_after_fix_summary.json`. Đây vẫn là kết quả development, chưa phải bằng
chứng khái quát hóa. Bước kế tiếp là khóa code và tạo validation paper-disjoint mới.
