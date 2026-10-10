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
