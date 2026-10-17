# Kết quả concept linking trên seed review 25 câu

## Trạng thái dữ liệu

Đây là kết quả **development descriptive** trên 25 câu ưu tiên của v17, gồm 6 câu dương
và 19 câu âm. Nhãn có trạng thái `assistant_pre_review`, chưa phải kết quả chính thức cho
đến khi chủ nhiệm đề tài xác nhận. Validation v16 và các held-out set không được sử dụng.

Tiêu chí gán nhãn giữ nguyên với benchmark concept-linking cũ: chỉ concept được biểu đạt
bởi chính câu hỏi; không nhìn evidence để suy ngược paper topic. Các câu hỏi chung chung
như “mô hình nào”, “baseline nào” hoặc “metric nào” là mẫu âm nếu concept cụ thể không
được nêu trong query.

## Trước cập nhật vocabulary

Ở sweep ngưỡng 0,45-0,70, cấu hình tốt nhất theo Hybrid F1 là 0,45:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 0,000 | 0,000 | 0,000 | 0,760 |
| Semantic | 0,071 | 0,167 | 0,100 | 0,640 |
| Hybrid | 0,071 | 0,167 | 0,100 | 0,640 |
| Phrase-first (0,45) | 0,125 | 0,167 | 0,143 | 0,600 |

Alias không nhận ra cách gọi rút gọn `embedding/embeddings`. Semantic ở ngưỡng thấp chỉ
tìm đúng 1/6 nhãn và tạo nhiều false positive; từ 0,50 trở lên không tìm đúng nhãn dương
nào. Phrase-first giảm số false positive so với whole-query Hybrid nhưng vẫn không đủ tốt.

## Thay đổi có bằng chứng lặp lại

Ba câu độc lập dùng `embedding` hoặc `embeddings` để chỉ `WordEmbedding`. Vì có bằng
chứng lặp lại trong development, hai alt label này được thêm đồng bộ vào TTL và OWL.

Không thêm alias cho các trường hợp chỉ xuất hiện một lần như `paired corpora`,
`bilingual models` hay `network architecture`. Chúng được giữ làm lỗi chưa giải quyết để
tránh chỉnh vocabulary theo từng câu.

## Sau cập nhật vocabulary

Ngưỡng 0,55 được chọn trên seed development theo Hybrid F1:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,000 | 0,500 | 0,667 | 0,880 |
| Semantic | 0,000 | 0,000 | 0,000 | 0,760 |
| Hybrid | 1,000 | 0,500 | 0,667 | 0,880 |
| Phrase-first | 0,750 | 0,500 | 0,600 | 0,880 |

Alias và Hybrid bắt đúng cả ba câu `WordEmbedding` và không tạo false positive.
Phrase-first giữ cùng recall nhưng thêm một false positive: `LanguageModel` cho câu hỏi
về “bilingual models”. Vì vậy phrase-first không được chọn thay alias/Hybrid ở mốc này.

## Kết luận

Kết quả củng cố hướng phát triển dựa trên nhãn: sửa alias có bằng chứng lặp lại hiệu quả
hơn tiếp tục giảm semantic threshold hoặc thêm heuristic rộng. Ba nhãn dương còn bỏ sót
(`MultilingualNaturalLanguageProcessing`, `ParallelCorpus`, `NeuralNetwork`) chỉ có một
ví dụ mỗi loại trong seed, nên cần thêm câu được review trước khi thay vocabulary.

Các file JSON trong cùng thư mục lưu đầy đủ sweep và prediction theo từng câu. Không dùng
seed này để tuyên bố khả năng khái quát hoặc làm kết quả final-test.

## Kiểm tra bằng chứng lặp lại trên 87 câu còn lại

Không dùng nhãn evidence để sửa query. Việc kiểm tra chỉ tìm các cách diễn đạt tương ứng
trong câu hỏi và cho thấy hai nhóm lặp lại độc lập:

- `multilingual models` đã được link đúng, trong khi `bilingual models` bị gán sai sang
  `LanguageModel`;
- `parallel corpus` đã được link đúng, trong khi `paired corpora` bị bỏ sót.

Do đó vocabulary được bổ sung các alt label `bilingual model(s)`, `multilingual model(s)`
cho `MultilingualNaturalLanguageProcessing` và `paired corpus/corpora` cho
`ParallelCorpus`. Các cách nói chỉ xuất hiện một lần như `network architecture`, `dropout`,
`formal language`, `RE model` vẫn không được thêm.

Sau cập nhật alias lặp lại, kết quả seed ở ngưỡng 0,55 là:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,000 | 0,833 | 0,909 | 0,960 |
| Semantic | 1,000 | 0,167 | 0,286 | 0,800 |
| Hybrid | 1,000 | 0,833 | 0,909 | 0,960 |
| Phrase-first | 1,000 | 0,833 | 0,909 | 0,960 |

Năm trong sáu nhãn dương được tìm đúng và không có false positive. Trường hợp còn bỏ sót
là `NeuralNetwork` từ “network architecture”; chưa có ví dụ lặp lại nên không thêm alias.
Kết quả này vẫn là development pre-review, chưa phải validation độc lập.
