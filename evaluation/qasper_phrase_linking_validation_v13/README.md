# Phrase-first query linking validation v13

## Protocol

- 20 QASPER papers, 1.184 chunks, 76 questions.
- Paper-disjoint from 285 papers used in earlier development/validation/final-test files.
- Candidate code frozen at `7b62b84`; evaluation harness at `ac96616`.
- Configuration selected only from the 16-question concept-linking development set.
- Evaluated exactly once on 2026-10-13. Final-test v4 remains sealed.

## Retrieval results at k=5

| Method | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| BM25 | 0,4151 | 0,3178 | 0,3056 |
| Semantic | 0,3890 | 0,3204 | 0,3044 |
| Hybrid | 0,4451 | 0,3371 | 0,3300 |
| Hybrid + Expansion | 0,4648 | 0,3498 | 0,3432 |
| Hybrid + Re-ranking | 0,4494 | 0,3476 | 0,3370 |
| Hybrid + Expansion + Re-ranking | **0,4692** | **0,3513** | **0,3456** |
| Hybrid + Ontology Graph | 0,4516 | 0,3469 | 0,3391 |

So với Hybrid, cấu hình kết hợp cải thiện 3 câu và cứu 2 câu vào top-5; đồng thời làm
xấu 1 câu và làm mất 1 câu khỏi top-5. Graph vẫn không được chọn vì có nhiều regression
hơn và điểm thấp hơn cấu hình kết hợp.

## Ontology coverage

- Query có concept: 18/76.
- Gold evidence có concept: 33/76.
- Query và gold evidence có quan hệ Ontology: 9/76.

Đây là bước tăng rõ so với tình trạng coverage rất thấp ở v11, nhưng vẫn còn 58/76 query
không có concept nên concept linking tiếp tục là giới hạn chính.

## Statistical check

Paired bootstrap 10.000 mẫu giữa Hybrid và cấu hình kết hợp:

| Metric | Difference | 95% CI | p two-sided |
|---|---:|---|---:|
| Precision@5 | +0,0026 | [-0,0079; +0,0132] | 0,8057 |
| Recall@5 | +0,0241 | [-0,0110; +0,0702] | 0,2408 |
| MRR@5 | +0,0143 | [-0,0055; +0,0414] | 0,2132 |
| nDCG@5 | +0,0157 | [-0,0053; +0,0426] | 0,1740 |

Mọi điểm trung bình đều tăng nhưng CI 95% còn chứa 0. Vì vậy kết luận đúng là candidate
khái quát theo hướng tích cực trên validation mới, chưa có đủ bằng chứng về ý nghĩa thống
kê ở mức 0,05. Candidate được bật cho demo và tiếp tục thu thập bằng chứng; final-test
không được mở ở bước này.
