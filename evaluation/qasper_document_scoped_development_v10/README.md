# QASPER document-scoped retrieval development v10

Development v10 thiết lập lại baseline theo đúng bản chất QASPER: mỗi câu hỏi chỉ truy hồi
trong bài báo nguồn được chỉ định bởi `paper_id`.

- 20 paper, 824 chunk và 74 câu hỏi có gold evidence.
- Loại 245 paper đã xuất hiện trong tất cả split trước, gồm validation v9.
- Overlap với các paper bị loại bằng 0.
- Benchmark code: commit `048a00d`.
- Hash dataset: `64708249727afe4264dacafd34d315a4d645573b67ff1bb9559fa1c9b9f5815a`.

Development v10 được phép dùng để phân tích và cải thiện. Validation v9 và final-test v4
không được chạy lại. Sau khi chọn thay đổi, phải tạo validation paper-disjoint mới.
