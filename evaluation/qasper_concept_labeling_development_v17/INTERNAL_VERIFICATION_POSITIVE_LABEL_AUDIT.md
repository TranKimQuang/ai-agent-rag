# Audit 10 nhãn dương của internal verification

## Cách kiểm tra

Mười nhãn dương `assistant_pre_review` được đối chiếu riêng theo ba nguồn: nội dung câu
hỏi, evidence QASPER và định nghĩa/quan hệ thật trong `ontology/document_qa.owl`. Quy tắc
gán nhãn vẫn là query-only; evidence chỉ dùng để kiểm tra ngữ cảnh, không dùng để đưa một
topic không xuất hiện trong câu hỏi vào nhãn.

Không chạy lại prediction, không đổi threshold và không sửa artifact kết quả đã khóa.

## Kết quả

| ID rút gọn | Concept cũ | Quyết định | Lý do chính |
|---|---|---|---|
| `3b7798a6` | MultilingualNaturalLanguageProcessing | Giữ | So sánh trực tiếp nhiều họ ngôn ngữ; evidence là cross-lingual. |
| `5cb3d696` | NaturalLanguageProcessing | Giữ | Text classification và NER là hai tác vụ NLP được nêu trực tiếp. |
| `86f24ecc` | NaturalLanguageProcessing | Giữ | Mã hóa thông tin cú pháp thuộc NLP; ontology chưa có lớp cú pháp hẹp hơn. |
| `14421b7a` | ArgumentMining | Loại | Xác định người thắng bằng xu hướng sentiment không phải nhận diện cấu trúc/lập luận. |
| `657edbf3` | LanguageModel | Giữ | Perplexity là metric đặc trưng của language modeling; evidence xác nhận ngữ cảnh này. |
| `790ed445` | MultilingualNaturalLanguageProcessing | Giữ | Code-switching là hiện tượng đa ngôn ngữ; evidence xử lý Hinglish. |
| `b67420da` | BidirectionalLanguageModel | Loại | BERT chưa được mô hình hóa hay ánh xạ tường minh vào concept này. |
| `d325a3c2` | NaturalLanguageProcessing | Giữ | Hypernymy/graded entailment là tác vụ lexical semantics trong NLP. |
| `f5cf8738` | BidirectionalLanguageModel | Loại | Nhắc BERT không đủ để thay bằng một concept rộng hơn khi ontology thiếu mapping. |
| `50f09a04` | MultilingualNaturalLanguageProcessing | Giữ | Câu hỏi mô tả ảnh hưởng xuyên ngôn ngữ; evidence xác nhận mô hình song ngữ. |

Tổng cộng: **giữ 7/10**, **loại 3/10**. Ba nhãn bị loại là lỗi gán quá rộng, đồng thời
chỉ ra hai khoảng trống vocabulary: `BERT` và bài toán dự đoán kết quả tranh luận dựa trên
sentiment.

## Ảnh hưởng tới kết quả đã khóa

- Kết quả prediction một lần trên 57 câu vẫn giữ nguyên và không bị tính lại hồi tố.
- Bảy nhãn dương còn hợp lệ đều nằm trong nhóm mà lần chạy đã bỏ sót, nên kết luận chính
  không đổi: linker hiện tại không khái quát được sang paraphrase khó.
- Precision/Recall/F1 vẫn có true positive bằng 0. Không tính lại exact match vì artifact
  khóa chỉ lưu metric tổng hợp, không lưu prediction từng câu.
- Tập 57 câu đã mở không được dùng để thêm alias, chỉnh threshold hay chọn mô hình.

File máy đọc tương ứng: `internal_verification_positive_label_audit.json`.
