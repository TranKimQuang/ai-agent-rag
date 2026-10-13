# Paired bootstrap: Hybrid vs hybrid_ontology

- Dataset: `evaluation/qasper_phrase_linking_validation_v13/qasper_validation.json`
- Số câu hỏi: 76
- Cutoff: k=5
- Bootstrap samples: 10000
- Seed: 20261013
- Query type intent: False

| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |
|---|---:|---:|---:|---|---:|---|
| precision_at_k | 0.134211 | 0.136842 | +0.002632 | [-0.007895, +0.013158] | 0.8057 | Không |
| recall_at_k | 0.445056 | 0.469179 | +0.024123 | [-0.010965, +0.070175] | 0.2408 | Không |
| mrr_at_k | 0.337061 | 0.351316 | +0.014254 | [-0.005482, +0.041447] | 0.2132 | Không |
| ndcg_at_k | 0.329970 | 0.345646 | +0.015676 | [-0.005303, +0.042592] | 0.1740 | Không |

## Diễn giải

Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; không được dùng để điều chỉnh theo held-out đã xem.
