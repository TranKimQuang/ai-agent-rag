# Validation configuration selection

- Questions: **35**
- Final-test status: **sealed_not_evaluated**
- Selected retrieval method: **hybrid**
- Query type intent: **False**
- Ontology weight: **0.000**
- Query expansion: **False**

| Configuration | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Hybrid baseline | 0.185714 | 0.192857 | 0.168921 |
| Best re-ranking candidate (weight 0.000, type-intent False) | 0.185714 | 0.192857 | 0.168921 |
| Best expansion candidate (type-intent False) | 0.185714 | 0.192857 | 0.168921 |

Validation did not show an nDCG@5 improvement from Ontology re-ranking or query expansion. Select the simpler Hybrid baseline and keep final-test sealed.
