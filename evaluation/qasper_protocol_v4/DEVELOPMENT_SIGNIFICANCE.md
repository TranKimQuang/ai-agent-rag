# Paired bootstrap: Hybrid vs Ontology re-ranking

- Dataset: `evaluation/qasper_protocol_v4/qasper_development.json`
- Số câu hỏi: 74
- Cutoff: k=5
- Bootstrap samples: 10000
- Seed: 20261003

| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |
|---|---:|---:|---:|---|---:|---|
| precision_at_k | 0.075676 | 0.075676 | +0.000000 | [+0.000000, +0.000000] | 1.0000 | Không |
| recall_at_k | 0.302703 | 0.302703 | +0.000000 | [+0.000000, +0.000000] | 1.0000 | Không |
| mrr_at_k | 0.207432 | 0.209234 | +0.001802 | [+0.000000, +0.005405] | 0.7489 | Không |
| ndcg_at_k | 0.211305 | 0.212834 | +0.001529 | [+0.000000, +0.004587] | 0.7489 | Không |

## Diễn giải

Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; không được dùng để điều chỉnh theo held-out đã xem.
