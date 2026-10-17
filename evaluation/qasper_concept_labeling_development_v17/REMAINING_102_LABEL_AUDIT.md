# Audit 102 nhãn còn lại của development v17

## Phạm vi và quy tắc

Phần audit này bao gồm toàn bộ 55 câu selection và 47 câu vốn được gán `NONE` trong
internal verification. Cùng với audit 10 nhãn dương trước đó, toàn bộ 112 câu đã được
kiểm tra ở mức nội bộ.

Quy tắc vẫn là query-only: evidence QASPER và bài báo gốc chỉ dùng để phân biệt nghĩa của
cụm từ, không dùng để đưa topic của cả bài báo vào một câu hỏi chung chung. Định nghĩa và
quan hệ trong `ontology/document_qa.owl` là chuẩn khái niệm cục bộ.

Không sửa các file nhãn nguồn, không chạy lại prediction và không thay cấu hình đã khóa.
Artifact JSON lưu quy tắc “giữ nguyên tất cả trừ năm ngoại lệ”, nên bao phủ đủ 102 hàng.

## Kết quả

- Giữ nguyên: **95/102** câu.
- Sửa nhãn: **7/102** câu.
- Loại 2 nhãn dương bị gán quá rộng và 2 nhãn nằm ngoài vocabulary đang hoạt động.
- Bổ sung 3 nhãn dương bị bỏ sót.
- Sau audit: 21 câu dương và 81 câu `NONE` trong nhóm 102 câu này.

### Bảy nhãn được sửa

| ID rút gọn | Nhãn cũ | Nhãn sau audit | Lý do |
|---|---|---|---|
| `e84ba95c` | TopicModeling | NONE | “Một model cho mỗi topic” là cách chia dữ liệu/model, không chứng minh dùng phương pháp topic modeling. Bài báo đang đánh giá summarization. |
| `38e11663` | Crowdsourcing | NONE | “Crowd” là ý kiến tổng hợp của người dùng mạng xã hội, không phải phương pháp thuê/thu thập nhãn bằng crowdsourcing. |
| `0fec9da2` | HumanEvaluation | NONE | Concept có trong ontology nhưng `retrievalEnabled=false`, nằm ngoài vocabulary của linker đang đánh giá. |
| `d5f8707d` | HumanEvaluation | NONE | Concept có trong ontology nhưng `retrievalEnabled=false`, nên hệ thống hiện tại không thể dự đoán nhãn này. |
| `6e76f114` | NONE | MultilingualNaturalLanguageProcessing | “Pivot language” là ngữ cảnh kỹ thuật xuyên ngôn ngữ, không phải một tên ngôn ngữ chung chung. |
| `191d4fe8` | NONE | MultilingualNaturalLanguageProcessing | Thử nghiệm trên một cặp ngôn ngữ nêu trực tiếp bối cảnh song/đa ngôn ngữ. |
| `ef07ec34` | NONE | MultilingualNaturalLanguageProcessing | Căn chỉnh tài liệu với bản dịch là bài toán biểu diễn xuyên ngôn ngữ; không phải WordEmbedding. |

Hai trường hợp loại nhãn được kiểm tra thêm bằng bài báo gốc: arXiv `1807.09671` mô tả
summarization bằng ILP, còn arXiv `1912.05066` dùng “crowd wisdom” từ sentiment trên
microblog. Hai thuật ngữ đó không khớp định nghĩa `TopicModeling` và `Crowdsourcing` trong
ontology cục bộ.

## Tổng hợp toàn bộ 112 câu

Kết hợp với audit 10 nhãn dương trước đó:

| Trạng thái sau audit | Số câu |
|---|---:|
| Có ít nhất một concept | 28 |
| `NONE` | 84 |
| Tổng | 112 |

Đây là bộ nhãn **assistant-audited**, chưa phải independent human gold. Muốn dùng làm số
liệu đánh giá chính thức, cần một người thứ hai kiểm tra độc lập hoặc ít nhất kiểm tra toàn
bộ 28 câu dương và một mẫu ngẫu nhiên đủ lớn trong 84 câu âm.

File máy đọc tương ứng: `remaining_102_label_audit.json`.
