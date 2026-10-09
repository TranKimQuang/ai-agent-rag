# QASPER context-aware Ontology scoring development v8

Development v8 là tập được phép dùng để phân tích lỗi và cải thiện cơ chế Ontology
re-ranking sau khi validation v7 không xác nhận mức cải thiện trung bình.

- 20 paper, 987 chunk và 73 câu hỏi có gold evidence.
- Loại 205 paper đã xuất hiện trong mọi split trước, gồm development v6 và validation v7.
- Overlap với các paper bị loại bằng 0.
- Seed chọn paper: `20261010`.
- Hash dataset: `6e3644e1c64d822ac5df4327af996a65fd83bd9b2e0e3451946ee08356e0817e`.

Quy trình:

1. Chạy baseline bằng cấu hình đã dùng trên v7.
2. Phân tích câu được cải thiện và câu bị làm xấu.
3. Thiết kế ontology bonus có điều kiện theo độ tin cậy, kiểu concept và ngữ cảnh.
4. Chỉ chọn cấu hình trên development v8.
5. Sau khi khóa code, tạo một validation paper-disjoint mới để đánh giá đúng một lần.

Không dùng lại validation v7 hoặc final-test v4 để tuning.

## Baseline trước sửa scoring

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,3342 | 0,2662 | 0,2599 |
| Hybrid + Expansion | 0,3342 | 0,2559 | 0,2521 |
| Hybrid + Re-ranking | 0,3205 | 0,2708 | 0,2580 |
| Hybrid + Expansion + Re-ranking | 0,3205 | 0,2674 | 0,2553 |

Re-ranking cải thiện 2 câu, cứu 1 câu, làm xấu 3 câu và làm mất 2 câu khỏi top-5.
Coverage cho thấy chỉ 7/73 query có concept, 26/73 gold evidence có concept và chỉ
3/73 cặp query-gold có quan hệ Ontology. Phân tích cho thấy các type cue chung như
`dataset` và `model` vẫn tạo bonus khi query không có concept chủ đề; đây là mục tiêu
cải thiện đầu tiên trên development v8.

## Candidate context gate

Candidate tại commit `4d5403a` không cấp bonus cho type cue chung nếu câu hỏi không có
concept chủ đề; Result-context bonus chỉ được dùng khi có concept chủ đề hoặc câu hỏi nêu
rõ result/performance.

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | 0,3342 | 0,2662 | 0,2599 |
| Re-ranking trước sửa | 0,3205 | 0,2708 | 0,2580 |
| Re-ranking với context gate | **0,3479** | **0,2708** | **0,2667** |

So với Hybrid, candidate cải thiện 1 câu, cứu 1 câu, làm xấu 1 câu và không làm mất
câu nào khỏi top-5. Câu còn bị tụt dùng evidence gián tiếp cho câu hỏi về Word2Vec,
trong khi một đoạn khác nhắc concept trực tiếp. Dừng tuning tại candidate này; bước kế
tiếp là khóa code và đánh giá đúng một lần trên validation paper-disjoint mới.
