# Rà soát gợi ý concept bằng LLM local

## Phạm vi

- Model: `qwen3:4b`, chạy local qua Ollama.
- Dữ liệu: 25/112 câu development v17 có semantic candidate liên hệ với concept trong
  gold evidence.
- Mục đích: hỗ trợ sắp xếp và giải thích hàng đợi review, không tạo gold label tự động.
- Ràng buộc: model chỉ được chọn trong tối đa ba candidate phía query và evidence;
  concept ngoài danh sách bị loại và confidence bị giới hạn còn 0,5.

## Kết quả

| Quan hệ do model đề xuất | Số câu |
|---|---:|
| exact | 8 |
| related | 2 |
| none | 6 |
| uncertain | 9 |
| **Tổng** | **25** |

- 12/25 câu được để trống concept phía query.
- 2/25 câu được để trống concept phía evidence.
- 7/25 câu chứa concept ngoài candidate list và đã bị constraint loại bỏ.

## Spot-check chất lượng

Reviewer nhận đúng một số trường hợp có biểu thức rõ như `embedding`/`WordEmbedding`.
Tuy nhiên, nó còn suy diễn topic từ paper hoặc evidence vào câu hỏi chung chung:

- câu hỏi “mô hình nào cho kết quả tốt nhất” bị gán `NeuralNetwork`;
- câu hỏi về baseline bị gán `LanguageModel`;
- câu hỏi hỏi ngôn ngữ của dữ liệu bị gán `NaturalLanguageProcessing`;
- một số giải thích nói concept “được nêu trực tiếp” dù từ đó chỉ có trong candidate
  metadata, không xuất hiện trong câu hỏi.

## Quyết định

Không tự động ghi các đề xuất vào `review_query_concepts`, `review_gold_concepts` hoặc
`review_relation`. Artifact được giữ lại để chứng minh đã thử phương án LLM-assisted
labeling và phát hiện giới hạn của model nhỏ. Nhãn dùng để đánh giá alias/semantic/
phrase-first vẫn phải được xác nhận thủ công trên development v17.

Validation v16 không tham gia thử nghiệm này và vẫn bị đóng đối với tuning.
