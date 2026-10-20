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
- `selection_strata.json`: strata ứng viên phục vụ kiểm toán selection bias.
- `manifest.json`: hash, danh sách loại trừ và trạng thái giao thức.

## Trạng thái

Đã chuẩn bị xong dữ liệu; đang chờ nhãn độc lập. Chưa chạy benchmark trên tập này.
