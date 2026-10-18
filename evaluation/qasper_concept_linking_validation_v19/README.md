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
- Nhãn độc lập đã khóa: 19 câu dương, 53 câu `NONE`, tổng 20 concept assignment.
- Prediction đã chạy đúng một lần ngày 18/10/2026; không tuning sau kết quả.
- Final test: vẫn niêm phong.

## File

- `qasper_validation.json`: 20 paper và 72 câu validation.
- `blinded_labeling_packet.csv`: câu hỏi, gold evidence và cột nhãn trống; không chứa
  dự đoán hay gợi ý của hệ thống.
- `active_concept_catalog.csv`: danh mục concept hợp lệ để người review tra cứu.
- `independent_labels_72.csv`: nhãn nguyên bản từ reviewer độc lập.
- `locked_labels_72.json`: nhãn đã kiểm tra, chuẩn hóa và khóa cho benchmark.
- `locked_result_once.json`: prediction và chỉ số của lần chạy duy nhất.
- `VALIDATION_RESULT.md`: tóm tắt kết quả và nhóm lỗi.
- `manifest.json`: hash, danh sách dữ liệu loại trừ và trạng thái khóa.

## Quy trình bắt buộc tiếp theo

1. Không sửa alias, threshold hoặc model dựa trên v19; mọi cải tiến sau đó phải chuyển
   sang development mới. Không mở final test ở bước này.

## Kết quả khóa

Hybrid 0,55 đạt Precision 0,7273, Recall 0,4000, F1 0,5161 và exact match 0,7917.
Kết quả thấp hơn development cho thấy nút thắt chính vẫn là recall và khả năng khái quát
sang cách diễn đạt/concept mới. Xem `VALIDATION_RESULT.md`; không dùng v19 để tuning.

