# QASPER document-scoped retrieval development v10

Development v10 thiết lập lại baseline theo đúng bản chất QASPER: mỗi câu hỏi chỉ truy hồi
trong bài báo nguồn được chỉ định bởi `paper_id`.

- 20 paper, 824 chunk và 74 câu hỏi có gold evidence.
- Loại 245 paper đã xuất hiện trong tất cả split trước, gồm validation v9.
- Overlap với các paper bị loại bằng 0.
- Benchmark code: commit `048a00d`.
- Hash dataset: `64708249727afe4264dacafd34d315a4d645573b67ff1bb9559fa1c9b9f5815a`.

Development v10 được phép dùng để phân tích và cải thiện. Validation v9 và final-test v4
không được chạy lại. Sau khi chọn thay đổi, phải tạo validation paper-disjoint mới.

## Baseline document-scoped

| Cấu hình | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid | **0,6164** | **0,3818** | **0,4140** |
| Hybrid + Expansion | 0,6097 | 0,3716 | 0,4041 |
| Hybrid + context-gated Re-ranking | 0,6164 | 0,3750 | 0,4091 |
| Hybrid + Expansion + Re-ranking | 0,6164 | 0,3716 | 0,4077 |

So với benchmark global trước đây, document scope đưa bài toán về đúng ngữ cảnh QASPER
và tăng mạnh Recall@5. Re-ranking hiện giữ Recall nhưng làm một câu tụt từ hạng 1 xuống
hạng 2. Coverage: 7/74 query có concept, 25/74 gold evidence có concept và 2/74 cặp
query-gold có quan hệ Ontology.

Bước thử nghiệm tiếp theo trên development: tận dụng entity type như Model/Dataset chỉ
khi retrieval đã được giới hạn trong đúng paper, với bonus nhỏ và có kiểm soát.

### Candidate entity-type bonus: loại

Thử bonus nhỏ 0,15 trước reliability scaling khi đã biết paper. Kết quả re-ranking:
Recall@5 0,6029, MRR@5 0,3723 và nDCG@5 0,4036; thấp hơn Hybrid ở cả ba chỉ số.
Candidate cải thiện 1 câu nhưng làm xấu 3 câu và làm mất 1 câu khỏi top-5. Vì vậy thay
đổi tại commit `f09754c` bị loại và code được đưa về context gate không cấp generic type
bonus. Kết quả âm vẫn được giữ để tránh lặp lại thí nghiệm.

### Contextualized retrieval: hai candidate đều bị loại

Đã tách `retrieval_text` khỏi `text`, nhờ đó phần dùng để lập chỉ mục có thể nhận thêm
ngữ cảnh nhưng evidence/citation vẫn giữ nguyên văn bản gốc. Ba cấu hình dùng cùng 824
chunk, 74 câu hỏi và gold IDs; benchmark đo đủ sáu phương pháp.

| Retrieval text | Hybrid Recall@5 | Hybrid MRR@5 | Hybrid nDCG@5 |
|---|---:|---:|---:|
| Section + passage (baseline) | **0,6164** | **0,3818** | **0,4140** |
| Title + section + passage | 0,5390 | 0,3446 | 0,3681 |
| Title + 80 từ abstract + section + passage | 0,4507 | 0,2962 | 0,3192 |

Title/abstract giống nhau bị lặp vào mọi chunk trong cùng paper, làm BM25 và đặc biệt
embedding khó phân biệt các passage. Hai candidate bị loại; pipeline chính tiếp tục dùng
passage gốc. Nếu thử contextual retrieval lần nữa, context phải đặc thù cho từng chunk
thay vì chỉ là metadata cấp paper.

### Graph concept-to-chunk retrieval: chưa được chọn

Đã bổ sung một kênh truy hồi trực tiếp từ concept của câu hỏi qua cạnh
`Chunk -> mentionsConcept -> Concept`, hợp nhất với Hybrid bằng RRF và vẫn giới hạn trong
đúng paper. Hai cấu hình đã được kiểm tra:

| Cấu hình graph | Recall@5 | MRR@5 | nDCG@5 | So với Hybrid |
|---|---:|---:|---:|---|
| Exact + quan hệ một bước | 0,6164 | 0,3795 | 0,4113 | 1 câu xấu đi |
| Chỉ exact concept | 0,6164 | 0,3818 | 0,4131 | 74/74 gold rank không đổi |

Quan hệ một bước bị loại vì query drift. Exact-only được giữ như cơ chế thử nghiệm an toàn
nhưng chưa chọn làm pipeline chính vì không cải thiện. Nút thắt được xác nhận là coverage:
chỉ 7/74 câu hỏi development link được concept, nên graph không có đủ tín hiệu để cứu các
retrieval miss.

### Query threshold riêng: chọn để kiểm tra trên validation mới

Threshold `0,55` cho câu hỏi được lấy từ bộ nhãn concept-linking validation độc lập
(precision 1,0; Hybrid F1 0,9412). Threshold chunk vẫn giữ `0,65`. Thay đổi này tăng
query coverage từ 7/74 lên 10/74 và số query-gold có quan hệ từ 2/74 lên 4/74.

Graph exact tăng MRR@5 từ 0,3818 lên **0,3851**, nDCG@5 từ 0,4140 lên **0,4158**;
một câu tăng gold rank từ 4 lên 2 và không câu nào xấu đi. Recall@5 giữ nguyên 0,6164.
Candidate được chọn để đánh giá đúng một lần trên validation paper-disjoint mới; chưa thay
pipeline mặc định trước khi có kết quả validation.
