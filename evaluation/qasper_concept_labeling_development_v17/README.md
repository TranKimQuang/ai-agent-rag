# QASPER concept-labeling development v17

## Mục tiêu

Tạo dữ liệu supervision riêng cho concept linking thay vì tiếp tục chỉnh heuristic theo
validation. Pool này gồm 30 paper, 1.483 chunk và 112 câu hỏi; không trùng với 325 paper
đã xuất hiện trong mọi development/validation/final-test trước đó.

Pool v17 **được phép gán nhãn và dùng để phát triển**. Không sao chép nhãn từ validation
v16 và không chạy lại v16 sau khi thay đổi mô hình.

## Baseline coverage

- Query có concept: 30/112.
- Gold evidence có concept: 57/112.
- Query và gold evidence có quan hệ Ontology: 7/112.

| Nhóm audit | Số câu |
|---|---:|
| Có concept hai phía nhưng thiếu quan hệ hoặc query link sai | 11 |
| Thiếu concept phía query | 39 |
| Thiếu concept phía gold evidence | 12 |
| Thiếu concept cả hai phía | 43 |
| Có quan hệ hữu ích, cần xác minh nhãn | 7 |

## File sử dụng

- `qasper_development.json`: dataset development gốc.
- `baseline_coverage.json`: coverage của pipeline hiện tại, không có retrieval tuning.
- `concept_error_audit.json`: đầy đủ Top-5 proposal cho query và gold evidence.
- `CONCEPT_LABELING_AUDIT.md`: bản đọc nhanh theo nhóm lỗi.
- `concept_labeling_review.csv`: hàng đợi review 112 câu, mở được bằng Excel.

CSV đã có concept hiện tại, concept trong evidence, proposal semantic, đoạn evidence và
gợi ý ưu tiên. Các cột `review_*` để trống có chủ ý vì proposal tự động không phải gold
label. Có 25 câu có candidate liên hệ được với concept evidence và nên được review trước;
55 câu cần kiểm tra lại concept của evidence trước khi đánh giá query.

## Quy trình tiếp theo

1. Review trước 25 hàng có `review_hint=review_candidate_related_to_gold`.
2. Ghi concept đúng hoặc `NONE` vào `review_query_concepts` và
   `review_gold_concepts`; ghi `exact`, `related`, `none` vào `review_relation`.
3. Tách nhãn thành train/dev nội bộ; không dùng validation v16 để lựa chọn.
4. Đo precision/recall/F1 của alias, semantic và phrase-first trước khi sửa Ontology.
5. Chỉ tạo validation paper-disjoint mới nếu concept-linking cải thiện rõ trên v17.
