# Concept linking trên 55 câu development pre-review

## Phạm vi

Kết quả gộp hai batch paper-disjoint với các tập cũ nhưng cùng thuộc development v17:

- Batch 1: 25 câu, 6 nhãn dương và 19 câu âm.
- Batch 2: 30 câu, 16 nhãn dương và 14 câu âm.
- Tổng: 55 câu và 22 nhãn concept dương.

Tất cả hàng vẫn có trạng thái `assistant_pre_review`; đây là development descriptive,
không phải validation hoặc final-test. Validation v16 và held-out cũ không được mở lại.

## Batch 2 độc lập

Nếu chọn riêng trên batch 2, Hybrid tốt nhất ở ngưỡng 0,50 với Precision 0,765,
Recall 0,813 và F1 0,788. Tuy nhiên ngưỡng này tạo các false positive do suy diễn quá rộng:

- `QuestionAnswering` từ “complete tasks”;
- `ROUGE` từ “evaluation metrics”;
- `MultipleChoiceQuestionAnswering` từ “label options”;
- `LanguageModel` từ “lexicon-based models”.

Phrase-first tại 0,50 giữ recall 0,813 nhưng Precision giảm còn 0,520 và F1 còn 0,634.
Vì vậy không chọn threshold hoặc phương pháp chỉ dựa trên batch 2.

## Kết quả gộp 55 câu

Sweep chung từ 0,45 đến 0,70 chọn ngưỡng 0,55 theo Hybrid F1:

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Alias | 1,000 | 0,545 | 0,706 | 0,818 |
| Semantic | 1,000 | 0,273 | 0,429 | 0,709 |
| Hybrid | **1,000** | **0,682** | **0,811** | **0,873** |
| Phrase-first | 0,643 | 0,818 | 0,720 | 0,782 |

Hybrid 0,55 tìm đúng 15/22 nhãn và không tạo false positive. Phrase-first tìm được
18/22 nhãn nhưng thêm nhiều concept sai, nên F1 và exact match đều thấp hơn Hybrid.

## Quyết định development

- Giữ threshold query concept-linking ở 0,55.
- Giữ Hybrid làm candidate hiện tại; không bật Phrase-first mặc định.
- Không giảm threshold xuống 0,50 chỉ để tăng recall.
- Không thêm alias dựa trên một câu đơn lẻ.
- Tiếp tục review thêm development trước khi khóa candidate cho validation mới.

Các JSON cùng thư mục lưu sweep đầy đủ và prediction theo từng câu. Kết quả chỉ được nâng
thành số liệu chính thức sau khi nhãn được chủ nhiệm đề tài xác nhận và candidate được kiểm
tra trên một validation paper-disjoint mới chạy đúng một lần.
