# QASPER context-aware Ontology scoring development v8

Development v8 là tập được phép dùng để phân tích lỗi và cải thiện cơ chế Ontology
re-ranking sau khi validation v7 không xác nhận mức cải thiện trung bình.

- 20 paper, 987 chunk và 73 câu hỏi có gold evidence.
- Loại 205 paper đã xuất hiện trong mọi split trước, gồm development v6 và validation v7.
- Overlap với các paper bị loại bằng 0.
- Seed chọn paper: `20261010`.
- Hash dataset: `6e3644e1c64d822ac5df4327af996a65fd83bd9b2e0e3451946ee08356e0817e`.

Quy trình:

1. Chạy baseline bằng cấu hình đã dùng trên v7.
2. Phân tích câu được cải thiện và câu bị làm xấu.
3. Thiết kế ontology bonus có điều kiện theo độ tin cậy, kiểu concept và ngữ cảnh.
4. Chỉ chọn cấu hình trên development v8.
5. Sau khi khóa code, tạo một validation paper-disjoint mới để đánh giá đúng một lần.

Không dùng lại validation v7 hoặc final-test v4 để tuning.
