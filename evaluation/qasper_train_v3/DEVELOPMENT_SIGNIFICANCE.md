# Paired bootstrap: Hybrid vs Ontology re-ranking

- Dataset: `evaluation/qasper_train_v3/qasper_train_development.json`
- Số câu hỏi: 78
- Cutoff: k=5
- Bootstrap samples: 10000
- Seed: 20261003

| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |
|---|---:|---:|---:|---|---:|---|
| precision_at_k | 0.079487 | 0.082051 | +0.002564 | [-0.005128, +0.012821] | 0.7719 | Không |
| recall_at_k | 0.299145 | 0.311966 | +0.012821 | [-0.025641, +0.064103] | 0.7725 | Không |
| mrr_at_k | 0.233120 | 0.238462 | +0.005342 | [-0.004487, +0.016239] | 0.3350 | Không |
| ndcg_at_k | 0.230575 | 0.237126 | +0.006551 | [-0.009919, +0.025360] | 0.4348 | Không |

## Diễn giải

Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; không được dùng để điều chỉnh theo held-out đã xem.
