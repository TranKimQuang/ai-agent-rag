# QASPER train development protocol

This directory contains two deterministic, paper-disjoint subsets derived from the official
AllenAI QASPER train split distributed through `allenai/qasper` on Hugging Face.

- Source file: `qasper/train/0000.parquet`, revision `refs/convert/parquet`.
- Source SHA-256: `9af08092ee26c4f700202c1f90d1592b662926f23f3a308a10ff0a53345e37fe`.
- Original dataset homepage: https://allenai.org/data/qasper
- License: CC BY 4.0.

## Splits

- Development: 20 papers, 1,049 paragraph chunks, 72 evidence-labelled questions.
- Held-out: 20 papers, 1,013 paragraph chunks, 72 evidence-labelled questions.

All 40 paper IDs are disjoint from the earlier ten-paper validation and ten-paper test subsets.
Only `qasper_train_development.json` may be used for vocabulary, threshold, weighting, or model
development. `qasper_train_heldout.json` must remain untouched until a new configuration and
evaluation protocol have been frozen.

## Initial development coverage

Before any vocabulary changes, only 1 of 72 development questions matched a local Ontology
concept. Gold evidence contained at least one concept for 20 questions, but only one
question/evidence pair received a non-zero Ontology relation score. The complete diagnostic is
stored in `development_coverage_baseline.json`. This confirms that query concept linking—not
retrieval weighting—is the first problem to solve in the new development cycle.

## Development vocabulary iteration 1

Eighteen recurring research concepts were added using development questions only, including word
segmentation, CNN, dynamic memory networks, causality extraction, grammatical error correction,
HMM/LSTM, word2vec, morphological tokenization, label propagation, distant supervision, and
machine translation. Coverage then changed as follows:

- Questions with a concept: 1/72 to 20/72.
- Gold evidence with a concept: 20/72 to 33/72.
- Question/evidence pairs with an Ontology relation: 1/72 to 12/72.

On 20 manually labelled development questions, Hybrid concept linking reached F1 0.9189 at
threshold 0.60, compared with Alias F1 0.8824. The remaining unlinked questions include many
generic requests about counts, baselines, and datasets; these should not be force-labelled merely
to inflate coverage. The held-out split remains untouched.

## Locked retrieval configuration v2

On the 72-question development split, Hybrid reached Recall@5 0.2037 and MRR@5 0.1648.
Ontology re-ranking kept Recall@5 at 0.2037 while increasing MRR@5 to 0.1718. Expansion reduced
Recall@5 to 0.1412 and is excluded from the primary configuration. Weight 0.05 was selected from
the development sweep; it improved one question and lost none. The configuration is frozen in
`locked_retrieval_config_v2.json`. The held-out split has not been evaluated.

## Held-out v2 result

The frozen v2 configuration was evaluated once on 72 held-out questions. Hybrid and all three
Ontology variants produced identical metrics: Recall@5 0.3264, MRR@5 0.2141, and nDCG@5
0.2271. Coverage analysis explains the equality: only 1/72 held-out questions matched a local
concept, 28/72 gold evidence sets contained a concept, and only 1/72 question/evidence pairs had
a non-zero Ontology relation.

This is retained as a negative generalization result. Development-specific aliases improved the
development split but did not transfer to unseen research topics. The next architecture iteration
must integrate semantic concept linking into retrieval itself; currently it is only evaluated by a
separate benchmark while retrieval still relies on exact aliases. No v2 parameter was changed
after observing held-out results.

Regenerate with:

```powershell
python -m scripts.prepare_qasper_parquet_subset `
  --input output/qasper-train-raw/qasper/train/0000.parquet `
  --output-dir evaluation/qasper_train `
  --exclude-dataset evaluation/qasper/qasper_validation.json `
  --exclude-dataset evaluation/qasper/qasper_test.json
```
