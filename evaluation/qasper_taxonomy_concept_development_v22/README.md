# QASPER taxonomy-focused concept development v22

## Mục tiêu

Tập này tạo hàng đợi gán nhãn có chủ đích cho các concept tham gia quan hệ
`skos:broader`. Nó được dùng để phát triển và kiểm tra cơ chế concept cha-con, không
được dùng như ước lượng không thiên lệch cho chất lượng concept linking tổng quát.

## Quy mô

- 37 paper, 1.858 chunk và 40 câu hỏi QASPER thật.
- 15 concept strata ứng viên; tối đa 5 ứng viên cho mỗi concept.
- 255 paper thuộc validation/final/held-out được loại hoàn toàn.
- 1.480 question ID đã xuất hiện trong các tập trước được loại.
- Không trùng paper với dữ liệu validation/final được bảo vệ.
- Có thể trùng paper với development cũ, nhưng câu hỏi luôn mới.

## Quy trình

1. Alias và semantic linker ở ngưỡng 0,50 chỉ tạo ứng viên cho hàng đợi review.
2. Người review dùng `blinded_labeling_packet.csv`; file này không chứa concept dự đoán.
3. `selection_strata.json` chỉ ghi lý do chọn mẫu, không phải gold label.
4. Phải khóa nhãn trước khi chạy dự đoán hoặc chọn cơ chế phóng chiếu cha-con.
5. Không tuning theo validation v19/v21 và không mở final test.

## File

- `qasper_taxonomy_development.json`: dữ liệu retrieval/evidence.
- `blinded_labeling_packet.csv`: 40 câu cần gán nhãn độc lập.
- `active_concept_catalog.csv`: danh mục concept hợp lệ.
- `taxonomy_concept_catalog.csv`: toàn bộ concept thuộc các cạnh taxonomy, dùng cho
  reviewer độc lập để giảm context mà không tiết lộ strata của từng câu.
- `selection_strata.json`: strata ứng viên phục vụ kiểm toán selection bias.
- `locked_labels_40.json`: nhãn development đã khóa trước prediction.
- `fixed_prediction_once.json`: lần chạy prediction cố định duy nhất sau khi khóa nhãn.
- `RESULT_SUMMARY.md`: kết quả exact, taxonomy-scoped và kết luận kỹ thuật.
- `manifest.json`: hash, danh sách loại trừ và trạng thái giao thức.

## Trạng thái

Đã khóa nhãn trước prediction: 17 câu dương, 23 câu `NONE`, 17 assignment. Nhãn do
Qwen3:4b review mù rồi được assistant audit, không phải human gold. Cấu hình cố định
đã chạy đúng một lần: whole-query F1 0,5714 và phrase-first F1 0,5789 trên toàn
vocabulary. Khi giới hạn theo 22 concept taxonomy được gán nhãn, F1 lần lượt là 0,7407
và 0,7586. Không có trường hợp cha–con trực tiếp nên projection không đem lại lợi ích.
