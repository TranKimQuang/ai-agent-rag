# Result-centric knowledge graph, audit và scoring v2

## Mục tiêu

Phiên bản v2 chuyển từ concept co-occurrence sang quan hệ thực nghiệm có phạm vi theo
paper và chunk:

`Paper -> Result -> Method/Model/Dataset/Metric/Value`

Mỗi `Result` giữ liên kết trực tiếp đến `Chunk` làm bằng chứng. Các tên thực thể chưa có
trong Ontology được tạo dưới dạng paper-scoped entity, không được thêm vào vocabulary toàn
cục và không tham gia query expansion.

## Audit trước khi sửa precision

Lần trích xuất đầu trên QASPER development tạo 52 `Result`. Toàn bộ 52 dòng được đọc thủ
công và lưu nhãn có thể tái tạo trong `result_context_review.json`.

| Hạng mục | Kết quả ban đầu |
|---|---:|
| Result đúng phạm vi | 32 |
| Không phải Result | 15 |
| Kết quả của prior work | 4 |
| Mơ hồ | 1 |
| Result precision, bỏ dòng mơ hồ | 62,75% |

Precision theo link trước sửa: Method 95,24%, Model 94,55%, Dataset 90,00%, Metric
93,88% và Value 85,00%. Các lỗi chính gồm: đoạn Settings/Related Work bị coi là Result,
`NER` bị coi là Model, citation token bị coi là Model, số lượng từ/length penalty bị coi
là metric value và kiến trúc `BLSTM` bị coi là Method.

Artifact gốc được giữ tại `result_context_audit_before_precision_fix.csv` và
`result_context_audit_before_precision_fix_summary.json`.

## Sửa bộ trích xuất

Các quy tắc sửa đều xuất phát từ nhóm lỗi audit, không dùng final-test:

1. loại các section Settings, Related Work, Method, Training Details, system/baseline setup;
2. loại đoạn chỉ mô tả bố cục paper hoặc kế hoạch thí nghiệm tương lai;
3. chỉ nhận giá trị số trong cùng câu có tên metric, nên không còn nhầm `3.2M` từ,
   `3%` training split hay length penalty `1.0`;
4. bổ sung AUC, ERR và H@k vào nhóm Metric;
5. chuyển nhãn kiến trúc như BLSTM/LSTM/CNN/RNN/BERT/GPT/Transformer/LR từ Method
   sang Model khi ngữ cảnh viết “... approach”.

Sau sửa, development tạo 39 `Result`: 38 dòng rõ ràng đúng phạm vi và 1 dòng mơ hồ do
trộn prior-work correction với audit của chính tác giả. Không còn dòng đã xác nhận sai.

| Role | Tổng link | Đúng | Sai | Mơ hồ | Precision đã review |
|---|---:|---:|---:|---:|---:|
| Method | 12 | 12 | 0 | 0 | 100,00% |
| Model | 43 | 43 | 0 | 0 | 100,00% |
| Dataset | 18 | 17 | 1 | 0 | 94,44% |
| Metric | 45 | 45 | 0 | 0 | 100,00% |
| Value | 13 | 13 | 0 | 0 | 100,00% |

Dataset còn một link `parallel corpus` đúng về loại dữ liệu nhưng quá chung để coi là một
dataset instance cụ thể; audit giữ nhãn sai thay vì tự làm đẹp số liệu. Vì các quy tắc được
thiết kế trên chính development audit, các precision trên là kết quả sửa lỗi development,
không được xem là ước lượng khả năng khái quát. Việc đó cần một validation paper split mới.

## Kết quả retrieval development sau sửa precision

Tập development gồm 74 câu; không dùng validation cũ hoặc final-test để chọn cấu hình.

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,3027 | 0,2074 | 0,2113 |
| Result-centric trước sửa, weight 0,30 | 0,3162 | 0,2137 | 0,2235 |
| Result-centric sau sửa, weight 0,30 | **0,3297** | **0,2182** | **0,2302** |

Sau sửa: 2 câu tăng hạng, 2 câu được cứu vào top 5, 1 câu giảm hạng và không có câu nào
bị mất khỏi top 5. Weight 0,30 được chọn trên development theo nDCG@5, nhưng chưa được
khóa làm cấu hình cuối trước khi có validation độc lập.

## Artifact

- `result_context_audit.csv`: audit hậu sửa với nhãn theo từng role.
- `result_context_audit_summary.json`: precision hậu sửa.
- `result_context_review.json`: nguồn nhãn thủ công và quy ước tính.
- `result_context_precision_fixed_development.json`: sweep trọng số hậu sửa.
- `result_context_audit_before_precision_fix.csv`: snapshot audit trước sửa.

## Quyết định

Audit đã hoàn thành và lỗi development đã được xử lý. Bước kế tiếp là tạo validation mới từ
paper chưa từng xuất hiện trong development/validation/held-out đã quan sát, chạy đúng một
lần để kiểm tra cả precision extraction và retrieval. Final-test v4 tiếp tục giữ
`sealed_not_evaluated`.

Validation này đã được chuẩn bị tại `evaluation/qasper_result_validation_v5/`: 20 paper,
1.109 chunk, 75 câu hỏi, loại 145 paper đã dùng và overlap bằng 0. Trạng thái vẫn là
`prepared_not_evaluated`; cần commit cấu hình trước khi chạy.
