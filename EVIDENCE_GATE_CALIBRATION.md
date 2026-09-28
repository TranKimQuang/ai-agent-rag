# Evidence Gate calibration — 27/09/2026

## Purpose

Calibrate the rule that decides whether retrieved passages are strong enough
to call the answer generator. This run uses only QASPER train-development data.
The held-out split was not loaded, evaluated or used for configuration.

## Method

- Source: `evaluation/qasper_train_v3/qasper_train_development.json`.
- Retrieval: document-scoped Hybrid + Ontology re-ranking, top 5.
- Model context: top 3 passages.
- The first 10 papers select thresholds; the remaining 10 papers verify the
  selected configuration without participating in selection.
- A correct-paper case is labelled supported when at least one QASPER gold
  evidence chunk appears in the top 3.
- Each question is also paired deterministically with another paper to create
  a synthetic unsupported case.
- 576 configurations were compared by balanced accuracy, then F1, precision
  and recall.

These are proxy labels for gate development. QASPER gold evidence may be
incomplete, and a non-gold passage is not automatically factually wrong.

## Selected thresholds

| Signal | Before | Selected |
|---|---:|---:|
| Ontology score | 0.65 | 0.80 |
| Ontology lexical overlap | 0 | 0 |
| Semantic score | 0.55 | 0.55 |
| Semantic lexical overlap | 2 | 2 |
| BM25 + semantic score | 0.30 | 0.40 |
| BM25 + semantic lexical overlap | 2 | 3 |

## Internal verification results

The second half contains 68 proxy examples, including 17 supported cases.

| Metric | Baseline | Selected |
|---|---:|---:|
| Accuracy | 0.412 | 0.574 |
| Balanced accuracy | 0.549 | 0.657 |
| Precision | 0.275 | 0.350 |
| Recall | 0.824 | 0.824 |
| Specificity | 0.275 | 0.490 |
| F1 | 0.412 | 0.491 |
| False positives | 37 | 26 |
| False negatives | 3 | 3 |

The selected gate rejects more weak/wrong-paper evidence without reducing
recall on this internal verification split. Precision remains low, so this is
an incremental safety improvement rather than a solved answerability model.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m scripts.calibrate_evidence_gate
```

The detailed local result is written to
`results/evidence_gate_calibration.json`. The next step is a larger manually
reviewed answer/citation evaluation, including naturally unanswerable
questions rather than relying only on wrong-paper negatives.

## Cross-encoder gate calibration — 28/09/2026

The optional `hybrid_ontology_cross_encoder` method changes candidate order,
but the original evidence gate did not treat its pairwise score as a calibrated
signal. A separate 20-configuration sweep used the same paper-separated
development selection/verification protocol and deterministic wrong-paper
negatives. Held-out data was not loaded.

| Verification metric | Initial 0.80 / overlap 1 | Selected 0.50 / overlap 3 |
|---|---:|---:|
| Balanced accuracy | 0.7130 | 0.7135 |
| Precision | 0.5135 | 0.5294 |
| Recall | 0.8261 | 0.7826 |
| Specificity | 0.6000 | 0.6444 |
| False positives | 18 | 16 |
| False negatives | 4 | 5 |

The selected configuration only marginally improves balanced accuracy. It is
therefore scoped to the optional cross-encoder method and does not change the
existing Agent retrieval/gate path. A targeted development check fixed one
previous false rejection with Answer-F1 0.902, left one weak case rejected,
and still refused both strict natural unanswerable questions. A third
answerable case passed the gate and cited gold evidence but received Answer-F1
0.0, confirming that answer generation remains a separate error source.

Detailed local artifacts:

- `results/cross_encoder_gate_calibration.json`
- `results/qasper_answer_evaluation_20260928T080847Z.json`
