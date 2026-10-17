# Hướng dẫn xác nhận nhãn concept độc lập

## Mục đích

Gói này dùng để người thứ hai gán nhãn mà không nhìn thấy nhãn của hệ thống hoặc nhãn
assistant đã audit. Đây là bước cần thiết trước khi dùng dữ liệu làm gold chính thức.

## File đưa cho reviewer

Chỉ gửi hai file sau:

1. `second_reviewer_blinded_112.csv`: 112 câu đã xáo thứ tự ổn định, có câu hỏi và đoạn
   evidence nhưng không có nhãn hiện tại.
2. `active_concept_catalog.csv`: danh sách concept đang thực sự được retrieval sử dụng,
   kèm tên và định nghĩa.

Không gửi `second_reviewer_reference_key.json` cho reviewer vì file đó chứa nhãn hiện tại
dùng để đối chiếu sau khi review hoàn tất.

## Cách điền

- Nếu câu hỏi trực tiếp biểu đạt một hoặc nhiều concept trong catalog, nhập `concept_id`
  vào cột `reviewer_concepts`; nhiều concept cách nhau bằng dấu chấm phẩy.
- Nếu không có concept phù hợp, điền `X` vào `reviewer_none`.
- Không suy nhãn chỉ từ evidence. Evidence chỉ giúp làm rõ ngữ cảnh/nghĩa của câu hỏi.
- Không gán concept quá rộng chỉ vì có từ chung như “model”, “dataset”, “evaluation”,
  “topic” hoặc “language”.
- Ghi trường hợp chưa chắc chắn vào `reviewer_notes`, không tự tạo concept ngoài catalog.

## Tiêu chí hoàn tất

Mỗi hàng phải có đúng một trong hai:

- `reviewer_concepts` khác rỗng; hoặc
- `reviewer_none = X`.

Sau khi nhận lại CSV, chạy bước reconciliation để tính agreement, liệt kê disagreement
và chỉ dùng nhãn đã giải quyết xong làm gold.

Script `scripts/reconcile_concept_second_review.py` đã sẵn sàng cho bước này. Script sẽ
từ chối file còn hàng trống, concept ngoài catalog, ID thiếu/trùng hoặc hàng vừa đánh
concept vừa đánh `NONE`; sau đó xuất agreement và toàn bộ disagreement để xử lý.
