# Paired bootstrap: Hybrid vs hybrid_ontology_rerank

- Dataset: `evaluation/qasper_document_topic_validation_v16/qasper_validation.json`
- Số câu hỏi: 77
- Cutoff: k=5
- Bootstrap samples: 10000
- Seed: 20261015
- Query type intent: False

| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |
|---|---:|---:|---:|---|---:|---|
| precision_at_k | 0.158442 | 0.161039 | +0.002597 | [-0.005195, +0.012987] | 0.7701 | Không |
| recall_at_k | 0.556926 | 0.558009 | +0.001082 | [-0.016234, +0.016234] | 0.9097 | Không |
| mrr_at_k | 0.403463 | 0.400433 | -0.003030 | [-0.029437, +0.022522] | 0.8135 | Không |
| ndcg_at_k | 0.406640 | 0.404487 | -0.002153 | [-0.020571, +0.014214] | 0.8373 | Không |

## Diễn giải

Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; không được dùng để điều chỉnh theo held-out đã xem.
