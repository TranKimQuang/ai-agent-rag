# Independent LLM second-review reconciliation

## Trạng thái

Reviewer ở thread độc lập đã hoàn thành đủ 112/112 câu bằng file mù, chỉ dùng catalog
concept đang hoạt động. File hợp lệ: không thiếu ID, không trùng ID, không có concept ngoài
catalog và mỗi hàng chọn đúng một trong `reviewer_concepts` hoặc `reviewer_none`.

Đây là **independent LLM review**, không được mô tả là human annotation.

## Kết quả đồng thuận

| Chỉ số | Kết quả |
|---|---:|
| Số câu | 112 |
| Exact agreement | 0,8214 |
| Agreement dương/âm | 0,8214 |
| Label precision so với audit đầu | 0,8333 |
| Label recall so với audit đầu | 0,3571 |
| Label F1 so với audit đầu | 0,5000 |
| Số câu bất đồng | 20 |

Audit đầu có 28 câu dương; reviewer độc lập chỉ gán 12 câu dương. Hai bên đồng ý ở 10
câu dương và 82 câu âm. Reviewer thêm 2 trường hợp `BidirectionalLanguageModel` do câu hỏi
nêu trực tiếp BERT; audit đầu có 18 nhãn dương mà reviewer không chấp nhận.

## Mẫu bất đồng chính

1. **Khái niệm quá cụ thể:** “embeddings” bị audit đầu ánh xạ thành `WordEmbedding`, còn
   reviewer không suy subtype khi câu hỏi không nói “word”.
2. **Suy từ hiện tượng sang lĩnh vực:** code-switching, language families, pivot language
   hoặc well-resourced language được audit đầu ánh xạ sang
   `MultilingualNaturalLanguageProcessing`, reviewer thường chọn `NONE`.
3. **Suy task con lên lớp cha:** dialogue acts, syntax, NER hoặc hypernymy được audit đầu
   ánh xạ lên `DiscourseAnalysis`/`NaturalLanguageProcessing`; reviewer yêu cầu biểu đạt
   trực tiếp hơn.
4. **Acronym rõ:** reviewer ánh xạ BERT sang `BidirectionalLanguageModel` ở hai câu mà
   audit đầu bỏ trống.

## Quyết định

Chưa tự động hợp nhất 20 câu bất đồng. Trước khi tạo gold cuối, cần áp dụng một quy tắc
adjudication thống nhất:

- chỉ gán subtype khi câu hỏi gọi đúng subtype hoặc alias trong catalog;
- cho phép ánh xạ task/hiện tượng lên concept cha chỉ khi ontology khai báo quan hệ rõ và
  chính sách gán nhãn đã ghi trước;
- không dùng evidence để thêm concept không được biểu đạt trong câu hỏi;
- BERT chỉ được ánh xạ nếu catalog/ontology khai báo alias hoặc mapping tương ứng.

Artifact chi tiết: `second_reviewer_reconciliation.json`. Danh sách 20 câu để xử lý tiếp
được xuất ở `second_reviewer_disagreements_20.csv`.
