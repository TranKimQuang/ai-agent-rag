# QASPER answer semantic and manual-review diagnostics — 28/09/2026

## Purpose

Token Answer-F1 is reproducible and follows QASPER-style evaluation, but it
penalizes correct paraphrases and cannot determine factual correctness by
itself. This diagnostic adds embedding similarity and exports a human-review
sheet. Neither is used to replace the official token or evidence metrics.

## Scope and results

- Input: the 22-question question-type-aware development run.
- Answerable questions: 20.
- Mean token Answer-F1: 0.433.
- Mean semantic similarity to the closest reference: 0.596.
- Pearson correlation between the two scores: 0.839.
- Cases flagged for manual review: 10/20.
- Low-F1 cases with semantic similarity at least 0.70: 2.
- Held-out data was not loaded.

The two clearest paraphrase cases were:

- “How are discourse embeddings analyzed?”: Answer-F1 0.258, semantic
  similarity 0.811. The prediction and citation both state that t-SNE
  clustering is used, matching the reference meaning.
- “What new metrics are suggested?”: Answer-F1 0.413, semantic similarity
  0.756. The prediction describes topology-based tests and the same-class
  closeness criterion contained in the reference.

## Why manual review is still necessary

Semantic similarity can also be high for an incomplete or nearby answer. A
citation can faithfully support the generated claim while that claim answers
the wrong aspect of the question. In the PAN 2017 case, the cited paragraph
supports the model's cross-year comparison, but the gold answer asks for the
shared-task ranking and margin over the second-best system. Citation grounding
and answer correctness must therefore be scored separately.

The exported CSV contains the question, prediction, references, cited chunks,
automatic metrics and three empty reviewer columns:

- `manual_answer_correct_0_1_2`: incorrect, partial, or correct.
- `manual_citation_supported_0_1`: whether citations support the generated claim.
- `manual_notes`: short justification.

This sheet is intended for transparent human annotation, not automatic
threshold tuning on the same development cases.

Detailed local artifacts:

- `results/qasper_answer_semantic_review.json`
- `results/qasper_answer_manual_review.csv`
