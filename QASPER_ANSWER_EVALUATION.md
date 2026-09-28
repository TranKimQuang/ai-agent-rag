# QASPER local answer baseline — 27/09/2026

## Scope

This is the first larger end-to-end development evaluation of the local
Qwen3:4b Agent. It covers retrieval, Ontology re-ranking, the calibrated
evidence gate, answer generation and server-owned citations.

- Retrieval data: 20 QASPER train-development papers already used for model
  development, one answerable question per paper.
- Natural unanswerable data: questions for which every available QASPER
  annotation says `Unanswerable`.
- Official source: `qasper-train-dev-v0.3.tgz`, SHA-256
  `a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a`.
- Model: local `qwen3:4b`; document-scoped Hybrid + Ontology re-ranking.
- Held-out data was not loaded or evaluated.

The requested sample was 20 answerable plus 5 naturally unanswerable
questions. Only two strict all-annotator-unanswerable questions were available
inside these selected 20 papers, so the actual run contains 22 questions.

## Metrics

Answer-F1 follows the official QASPER/SQuAD-style normalized token overlap and
takes the best score across reference annotations. Evidence-F1 compares cited
paragraph IDs with each annotation's evidence and also takes the best match.
An Agent refusal is evaluated as the QASPER answer `Unanswerable`.

| Metric | Result |
|---|---:|
| Answerable questions | 20 |
| Answered / refused | 15 / 5 |
| Answer-F1 on answerable questions | 0.246 |
| Evidence-F1 on answerable questions | 0.358 |
| Citation precision on answerable questions | 0.300 |
| Citation recall on answerable questions | 0.375 |
| Strict natural unanswerable questions | 2 |
| Correctly refused | 2/2 |
| Generation errors | 0 |
| Mean end-to-end time | 13.081 seconds |
| First cold case | 67.313 seconds |

Across all 22 questions, including the two correctly refused cases,
Answer-F1 is 0.315 and Evidence-F1 is 0.417. Those combined values are higher
because correct unanswerable refusals score 1.0; the answerable-only values are
the more informative baseline for answer quality.

## Findings

- The Agent can complete the full local pipeline without generation errors.
- It safely refused both strict natural unanswerable questions in this sample.
- Retrieval/citation remains the main bottleneck: several fluent answers cited
  same-paper passages outside the QASPER gold evidence.
- Boolean questions expose an answer-format weakness. The model often explains
  the evidence without beginning with the reference `Yes` or `No`, producing
  low token F1 even when its explanation points in the correct direction.
- Five answerable questions were rejected by the evidence gate. This is safer
  than unsupported generation but lowers answer coverage.

## Limitations and next step

This is a deterministic development sample, not independent human scoring and
not a held-out result. QASPER references can disagree (some questions contain
both an answer and an unanswerable annotation), and token F1 does not fully
measure semantic correctness.

The next iteration should improve direct-answer formatting, especially
yes/no questions, and perform a manual error analysis separating retrieval
misses, gate rejections, answer errors and citation errors. Any revised
configuration must be selected on development before the held-out set is run.

Detailed local artifact:
`results/qasper_answer_evaluation_20260927T115655Z.json`.

## Development follow-up: direct-answer prompt

The seven baseline cases classified as answer content/format errors were run
again after requiring the model to begin with the direct answer: `Yes`/`No`
for boolean questions and the requested number, name, task, metric or list for
short-answer questions.

| Metric on the same 7 cases | Baseline prompt | Direct-answer prompt |
|---|---:|---:|
| Answer-F1 | 0.201 | 0.563 |
| Evidence-F1 | 0.690 | 0.881 |
| Citation precision | 0.643 | 0.929 |
| Citation recall | 0.857 | 0.857 |

All seven cases were answered without generation errors; two reached
Answer-F1 1.0. This is a targeted development comparison selected from known
errors, so it demonstrates that the formatting fix works on those cases but is
not an unbiased replacement for the 22-question baseline. Retrieval misses and
evidence-gate rejections remain separate problems.

Detailed local artifact:
`results/qasper_answer_evaluation_20260927T120906Z.json`.

## Full direct-answer and cross-encoder comparison

The full 22-question development sample was run with the revised prompt under
both the existing retrieval method and the optional cross-encoder method.
Keeping the prompt fixed isolates the retrieval change.

| Answerable metric | Existing retrieval | Cross-encoder |
|---|---:|---:|
| Answer-F1 | **0.349** | 0.292 |
| Evidence-F1 | 0.425 | **0.450** |
| Citation precision | 0.400 | **0.425** |
| Citation recall | 0.375 | **0.425** |
| Answered | **16/20** | 15/20 |

Both correctly refused 2/2 strict unanswerable questions. Although the
cross-encoder increased retrieval Recall@5 from 0.600 to 0.850 in the separate
retrieval experiment, it did not increase end-to-end Answer-F1 and added about
2.9 seconds per case. It therefore remains an optional ablation method rather
than the Agent default.

## Question-type-aware answer formatting — 28/09/2026

The generator now receives a deterministic answer format inferred only from
the question wording: `boolean`, `number`, `short_phrase_or_list`, or
`explanation`. This prevents non-boolean questions such as “how are ...” from
being answered with `Yes`, and asks factoid/list questions to omit a repeated
question preamble.

The same 22-question development sample was run with unchanged default
retrieval and evidence-gate settings:

| Answerable metric | Direct-answer prompt | Question-type-aware prompt |
|---|---:|---:|
| Answer-F1 | 0.349 | **0.433** |
| Evidence-F1 | **0.425** | 0.417 |
| Citation precision | 0.400 | 0.400 |
| Citation recall | 0.375 | 0.375 |
| Answered | 16/20 | **17/20** |
| Mean time, all 22 cases | **9.738 s** | 10.508 s |

Both configurations correctly refused 2/2 strict natural unanswerable
questions and had no generation errors. The Answer-F1 gain is substantial,
while the small Evidence-F1 decrease shows that formatting does not solve
retrieval/citation selection. No held-out data was loaded.

Detailed local artifact:
`results/qasper_answer_evaluation_20260928T082453Z.json`.
