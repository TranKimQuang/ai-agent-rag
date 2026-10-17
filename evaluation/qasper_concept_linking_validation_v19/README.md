# QASPER concept-linking validation v19

## Mục tiêu

Đây là tập validation mới để kiểm tra khả năng khái quát của cấu hình concept linking
đã chọn trên development v18. Tập gồm 20 paper, 1.029 chunk và 72 câu hỏi có gold
evidence. Không có paper nào trùng với 355 paper đã xuất hiện trong các tập trước.

## Trạng thái khóa

- Cấu hình trước validation: Hybrid concept linking, threshold 0,55.
- Ontology đã loại các alias quá rộng `embedding/embeddings` và
  `paired corpus/corpora`; chỉ giữ cụm từ chỉ rõ subtype.
- Code/config tham chiếu trước khi tạo tập: commit `7d8adea`.
- Nhãn: chưa có, đang chờ gán độc lập.
- Prediction: **chưa chạy**.
- Final test: vẫn niêm phong.

## File

- `qasper_validation.json`: 20 paper và 72 câu validation.
- `blinded_labeling_packet.csv`: câu hỏi, gold evidence và cột nhãn trống; không chứa
  dự đoán hay gợi ý của hệ thống.
- `active_concept_catalog.csv`: danh mục concept hợp lệ để người review tra cứu.
- `manifest.json`: hash, danh sách dữ liệu loại trừ và trạng thái khóa.

## Quy trình bắt buộc tiếp theo

1. Gán `reviewer_concepts` bằng ID trong catalog, ngăn cách bằng `|`; nếu không có
   concept được diễn đạt trong câu hỏi thì ghi `reviewer_none=1`.
2. Khóa file nhãn và hash trước khi chạy bất kỳ prediction nào.
3. Chạy đúng một lần cấu hình Hybrid 0,55; báo cáo Precision, Recall, F1 và exact match.
4. Không sửa alias, threshold hoặc model dựa trên v19; mọi cải tiến sau đó phải chuyển
   sang development mới. Không mở final test ở bước này.

