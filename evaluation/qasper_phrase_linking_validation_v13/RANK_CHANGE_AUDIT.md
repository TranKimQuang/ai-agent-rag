# Rank-change audit

Audit mô tả bảy câu có gold rank thay đổi giữa Hybrid và Phrase-first + Expansion +
Re-ranking. Đây là phân tích sau validation, không dùng để tuning hoặc chạy lại v13.

| Query | Query concepts | Hybrid -> Candidate | Nhận định |
|---|---|---:|---|
| pretrained language models besides BERT | LanguageModel | 5 -> 1 | Đúng; exact concept có trong gold evidence. |
| CNN injected into recurrent units | ConvolutionalNeuralNetwork | 4 -> ngoài top-5 | Concept đúng nhưng expansion làm trôi khỏi evidence; re-ranking riêng giữ hạng 4. |
| coreference chains in MT outputs | CooccurrenceMatrix | 3 -> 2 | Link sai do gần hình thức/ngữ nghĩa; điểm tăng là ngẫu nhiên, không được tính là thành công Ontology. |
| three neural machine translation systems | NeuralMachineTranslation, PhraseBasedMachineTranslation | 2 -> 3 | NMT đúng nhưng concept phụ quá cụ thể gây drift. |
| active learning model | TransferLearning | 4 -> 3 | Link sai/vocabulary gap; cải thiện rank không chứng minh Ontology đúng. |
| crowdsourcing platform | Crowdsourcing | ngoài top-5 -> 4 | Query concept hợp lý; expansion cứu evidence dù chunk gold chưa được gán concept. |
| knowledge extraction performance | InformationRetrieval | ngoài top-5 -> 5 | Concept khá rộng; cần review/cross-encoder trước khi coi là link đúng. |

## Kết luận kỹ thuật

- Re-ranking dựa trên concept chính xác an toàn hơn expansion: validation ghi nhận một câu
  cải thiện và không câu nào xấu đi.
- Expansion tạo mức tăng tổng thể lớn hơn nhưng là nguồn của cả hai regression và một số
  “cải thiện” dựa trên concept sai.
- Bước tiếp theo không phải hạ threshold hay thêm graph edge. Cần xây candidate re-ranker
  đọc đồng thời query/phrase và concept label + definition; đồng thời thêm `ActiveLearning`
  và coreference vào hàng đợi gán nhãn development, không thêm trực tiếp từ validation.
- Validation v13 đã dùng xong và không được chạy lại để chọn threshold/candidate.
