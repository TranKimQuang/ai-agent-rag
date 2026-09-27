# QASPER cross-encoder reranker development experiment — 27/09/2026

## Purpose

The QASPER answer baseline contained eight retrieval misses at top 5. A
diagnostic run to rank 20 showed that seven of those eight gold evidence
paragraphs were still present in the candidate set. This experiment therefore
tests a small cross-encoder as a second-stage reranker instead of sending more
noisy chunks directly to the LLM.

## Configuration

- Data: the same 20 answerable development questions used by the local answer
  baseline, one question per development paper.
- Candidate generator: document-scoped Hybrid + Ontology re-ranking.
- Candidate depth: 20; evaluated output depth: 5.
- Reranker: `cross-encoder/ms-marco-MiniLM-L6-v2`.
- Runtime: CPU because the project's current PyTorch wheel is CPU-only. Ollama
  remains able to use the GPU independently.
- Held-out data was not loaded or evaluated.

## Results

| Metric | Hybrid + Ontology | Cross-encoder reranked |
|---|---:|---:|
| Recall@5 | 0.600 | 0.850 |
| MRR | 0.424 | 0.566 |

Candidate recall@20 was 0.950, confirming that ranking rather than candidate
generation was the dominant problem in this sample. The reranker recovered
five additional top-5 hits.

## Interpretation and limitations

This is a promising development result, not a held-out result and not yet the
new production configuration. The sample was already used for answer-error
analysis, so it is unsuitable for an unbiased final claim. The next step is to
integrate the reranker as a separate optional retrieval method, preserve the
existing methods for ablation, and measure its effect on end-to-end answers
before designing a fresh evaluation protocol.

Detailed local artifact: `results/qasper_cross_encoder_reranker.json`.
