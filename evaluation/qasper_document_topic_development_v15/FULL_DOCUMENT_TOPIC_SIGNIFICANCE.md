# Paired bootstrap: Hybrid vs hybrid_ontology_rerank

- Dataset: `evaluation/qasper_document_scoped_development_v10/qasper_development.json`
- Số câu hỏi: 74
- Cutoff: k=5
- Bootstrap samples: 10000
- Seed: 20261014
- Query type intent: False

| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |
|---|---:|---:|---:|---|---:|---|
| precision_at_k | 0.178378 | 0.178378 | +0.000000 | [+0.000000, +0.000000] | 1.0000 | Không |
| recall_at_k | 0.616441 | 0.616441 | +0.000000 | [+0.000000, +0.000000] | 1.0000 | Không |
| mrr_at_k | 0.381757 | 0.384009 | +0.002252 | [-0.004054, +0.010811] | 0.6485 | Không |
| ndcg_at_k | 0.414050 | 0.415819 | +0.001769 | [-0.003410, +0.008711] | 0.6517 | Không |

## Diễn giải

Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; không được dùng để điều chỉnh theo held-out đã xem.
