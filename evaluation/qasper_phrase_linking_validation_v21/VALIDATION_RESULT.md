# Kết quả phrase-linking validation v21

## Protocol

- 30 paper, 49 câu, không trùng 405 paper trước đó.
- Nhãn độc lập được commit tại `f2d3388` trước prediction.
- Candidate cố định từ development: phrase-first Hybrid, threshold 0,65, margin 0,03,
  limit 5.
- Chạy đúng một lần, không quét cấu hình trên v21.

## Kết quả

| Phương pháp | Precision | Recall | F1 | Exact match |
|---|---:|---:|---:|---:|
| Whole-query Hybrid | **1,0000** | 0,1000 | **0,1818** | **0,6531** |
| Phrase-first Hybrid | 0,6667 | 0,1000 | 0,1739 | 0,6327 |

Phrase-first chỉ tạo thêm một thay đổi: gán sai `DatasetBias` cho câu hỏi về
“interpretive biases”. Nó không tìm thêm gold concept nào. Candidate do đó bị loại.

## Kết luận

Kết quả tiếp tục xác nhận vấn đề không thể giải quyết chỉ bằng threshold, alias hay tách
phrase. Concept inventory hiện quá rộng ở một số nhãn (`NaturalLanguageProcessing`) và
quá thưa ví dụ ở các nhãn cụ thể; semantic similarity không đủ để phân biệt quan hệ
taxonomy và ngữ cảnh sử dụng.

Không tuning theo v21 và không chạy final test. Hướng tiếp theo nên là thu hẹp bài toán
concept linking về một tập concept trọng tâm có đủ dữ liệu dương, hoặc dùng một dataset
entity-linking chuyên biệt; không tiếp tục tạo validation tuần tự trên phần QASPER còn lại.

