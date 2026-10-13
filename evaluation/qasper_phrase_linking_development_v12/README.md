# Phrase-first query concept linking development v12

## Mục tiêu

Thử nghiệm này xử lý nút thắt coverage của query concept linking mà không thay đổi
vocabulary, graph weight hoặc final-test. Candidate được đánh giá trên bộ 16 câu đã có
nhãn concept độc lập tại `evaluation/qasper/concept_linking_validation.json`.

## Candidate

1. Giữ exact alias ở confidence 1,0.
2. Bỏ question scaffolding và tách các content phrase/ngram dài 2-5 từ.
3. Dùng bi-encoder hiện có lấy Top-2 concept cho từng phrase.
4. Chỉ nhận Top-1 nếu score >= 0,55 và cách Top-2 ít nhất 0,03.
5. Nếu đã có exact alias, semantic concept bổ sung phải đạt ít nhất 0,60.

Candidate là opt-in qua `query_phrase_linking=True`; pipeline mặc định chưa thay đổi.

## Kết quả development

| Cấu hình | Precision | Recall | F1 | Exact match | Câu có link |
|---|---:|---:|---:|---:|---:|
| Whole-query Hybrid | 0,8000 | 0,8889 | 0,8421 | 0,8125 | 14/16 |
| Phrase-first Hybrid | **0,9444** | **0,9444** | **0,9444** | **0,8750** | 14/16 |

Thay đổi có ích quan sát được:

- Bổ sung đúng `ArgumentMining` cho câu hỏi về argument components.
- Loại các semantic concept nhiễu của whole-query linker quanh câu hỏi về recurrent
  neural network; còn lại exact alias `NeuralNetwork` và `RecurrentNeuralNetwork`.

Chi tiết từng câu, score và source nằm trong `phrase_linking_margin_003.json`.

## Quyết định

Candidate vượt development gate nhưng chưa đủ để thay pipeline mặc định. Không dùng lại
validation v11 để tune. Cần commit/khóa code và đánh giá đúng một lần trên một split QASPER
paper-disjoint mới; final-test v4 tiếp tục sealed.
