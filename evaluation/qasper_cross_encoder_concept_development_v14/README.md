# Cross-encoder concept candidate development v14

## Mục tiêu

Kiểm tra liệu cross-encoder đang có trong dự án có thể xếp lại Top-5 semantic concept
candidates và giảm query drift hay không. Chỉ dùng 16 câu concept-linking development;
không đọc hoặc chạy lại validation v13/final-test.

## Cấu hình

- Candidate generator: phrase-first bi-encoder, semantic threshold 0,55.
- Candidate depth: 5 concept cho mỗi phrase.
- Reranker: `cross-encoder/ms-marco-MiniLM-L6-v2` chạy CPU.
- Grid development: cross threshold {-4, -2, 0, 2, 4}; Top-1/Top-2 margin
  {0, 0,5, 1, 2}.
- Exact aliases luôn được giữ; semantic concept phụ vẫn cần score bi-encoder >= 0,60.

## Kết quả

| Candidate | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Phrase-first | 0,9444 | 0,9444 | 0,9444 | 0,8750 |
| Cross-encoder tốt nhất | 0,9444 | 0,9444 | 0,9444 | 0,8750 |

Cross-encoder chỉ giữ được kết quả ngang baseline khi threshold rất lỏng (-4). Threshold
cao hơn bắt đầu loại concept đúng và làm recall giảm. Không có cấu hình nào vượt phrase-first.

## Quyết định

Không tích hợp model MS-MARCO này vào query concept linker. Model được huấn luyện cho
passage relevance, không phải phân biệt các concept ontology gần nhau; kết quả thực nghiệm
phù hợp với giới hạn đó. Hạ tầng `score_pairs` và audit Top-k được giữ để có thể thử một
model entity-linking/NLI phù hợp hơn sau này. Pipeline demo tiếp tục dùng phrase-first đã
validation; validation v13 và final-test không chạy lại.
