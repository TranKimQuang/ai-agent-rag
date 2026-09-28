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

## Expanded 50-answerable diagnostic

The same diagnostic was applied to the expanded development run without
loading held-out data:

- Answerable questions: 50.
- Mean token Answer-F1: 0.314.
- Mean semantic similarity to the closest reference: 0.517.
- Pearson correlation: 0.839.
- Cases flagged for manual review: 26/50.
- Low-F1 cases with semantic similarity at least 0.70: 2.

The 26-case CSV is the working set for reporting human answer correctness and
citation support separately. The lower means compared with the 20-question
sample show why the expanded sample is a better development checkpoint; they
must not be presented as a held-out score or replaced by semantic similarity.

Expanded local artifacts:

- `results/qasper_answer_semantic_review_50.json`
- `results/qasper_answer_manual_review_50.csv`

## AI-assisted pre-review of the 26 flagged cases

To reduce reviewer effort, the 26 flagged cases now include three separate
`suggested_*` columns with an initial label and a short rationale. The official
`manual_*` columns remain empty by design: these suggestions are produced by an
AI assistant and are not independent human evaluation.

The suggested distribution is 10 correct, 8 partial and 8 incorrect answers.
For 22/26 cases (84.6%), the citation supports the generated claim. This high
support rate must not be confused with answer correctness: several citations
faithfully support a nearby or incomplete claim that does not answer the
question asked. The PAN competitor comparison and Reddit community-selection
cases are clear examples.

Before using human-scored numbers in a report, the student should inspect each
row in `results/qasper_answer_manual_review_50.csv`, copy or revise the
suggestion into the corresponding `manual_*` columns, and add initials/date.
The reproducible suggestion source is tracked at
`evaluation/qasper_answer_review_suggestions.json`.
