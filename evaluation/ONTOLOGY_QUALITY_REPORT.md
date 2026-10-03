# Ontology quality evaluation

## 1. Reasoner consistency

- Reasoner: OWL-RL (owlrl)
- Kết quả: **PASS**
- Triple trước suy luận: 550
- Triple sau suy luận: 1616
- Triple suy ra: 1066
- Số lỗi consistency: 0

## 2. Thống kê mô hình

- Class: 14
- Object property: 25
- Datatype property: 9
- Individual: 73
- Property có domain: 34
- Property có range: 34
- Object property có inverse: 8

## 3. Competency questions

| ID | Câu hỏi | Số dòng tối thiểu | Số dòng thực tế | Kết quả |
|---|---|---:|---:|---|
| CQ01 | Bài báo nào sử dụng một dataset cụ thể? | 1 | 1 | PASS |
| CQ02 | Phương pháp nào giải quyết một task cụ thể? | 1 | 1 | PASS |
| CQ03 | Chunk nào nhắc đến một concept cụ thể? | 1 | 1 | PASS |
| CQ04 | Những concept nào có quan hệ trực tiếp với một concept? | 1 | 91 | PASS |
| CQ05 | Từ paper có thể truy vết đến chunk và concept bằng đường đi nào? | 1 | 1 | PASS |
| CQ06 | Bài báo được đánh giá bằng metric nào? | 1 | 1 | PASS |
| CQ07 | Một paper chứa những section và chunk nào? | 1 | 1 | PASS |
| CQ08 | Concept nào có concept rộng hơn trong phân cấp? | 1 | 21 | PASS |
| CQ09 | Hybrid Search có liên quan đến những phương pháp retrieval nào? | 3 | 3 | PASS |
| CQ10 | Chunk nào là evidence cho một kết quả? | 1 | 1 | PASS |

## 4. CSO mapping

- `skos:exactMatch`: 2
- `skos:closeMatch`: 3
- Đã rà soát thủ công URI và phạm vi ánh xạ với CSO 3.5 ngày 03/10/2026; reasoner chỉ kiểm tra mô hình nội bộ và không tự chứng minh tương đương ngữ nghĩa với nguồn bên ngoài.

| Concept cục bộ | Quan hệ | URI bên ngoài |
|---|---|---|
| InformationRetrieval | exactMatch | https://cso.kmi.open.ac.uk/topics/information_retrieval |
| NaturalLanguageProcessing | exactMatch | https://cso.kmi.open.ac.uk/topics/natural_language_processing |
| QuestionAnswering | closeMatch | https://cso.kmi.open.ac.uk/topics/question_answering |
| RetrievalAugmentedGeneration | closeMatch | https://cso.kmi.open.ac.uk/topics/retrieval-augmented_generation |
| SemanticSearch | closeMatch | https://cso.kmi.open.ac.uk/topics/semantic_search |
