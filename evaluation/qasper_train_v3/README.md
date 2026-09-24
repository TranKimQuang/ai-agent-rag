# QASPER train protocol v3

This directory is the evaluation protocol created after integrating semantic concept linking into
the real retrieval pipeline. Both subsets come from the official AllenAI QASPER train split.

- Source file: `qasper/train/0000.parquet`, revision `refs/convert/parquet`.
- Source SHA-256: `9af08092ee26c4f700202c1f90d1592b662926f23f3a308a10ff0a53345e37fe`.
- Dataset homepage: https://allenai.org/data/qasper
- License: CC BY 4.0.

## Splits

- Development: 20 papers, 910 paragraph chunks, 78 evidence-labelled questions.
- Held-out: 20 papers, 1,201 paragraph chunks, 70 evidence-labelled questions.
- Development SHA-256: `ffd6ffb5afbcf03f4ea7f0c3f4feb4c81faefddf3b646a7f07bbe9fd75f0822a`.
- Held-out SHA-256: `2f61aa1b0e97e5dbc26ee798120cb7ffb9e5c7fa618fe025ed2399632d2b12cd`.

The two v3 subsets are paper-disjoint. They are also disjoint from all 60 papers in the earlier
QASPER validation, test, train-development, and train-held-out subsets.

## Evaluation rule

Only `qasper_train_development.json` may be used for error analysis, threshold selection,
vocabulary changes, or weight selection. Do not run or inspect retrieval results for
`qasper_train_heldout.json` until the v3 configuration is frozen in a committed configuration
file. After that point, run the held-out evaluation once and report the result without tuning on
it.

Regenerate from the verified source with:

```powershell
python -m scripts.prepare_qasper_parquet_subset `
  --input output/qasper-v3-source/0000.parquet `
  --output-dir evaluation/qasper_train_v3 `
  --papers 40 `
  --development-papers 20 `
  --exclude-dataset evaluation/qasper/qasper_validation.json `
  --exclude-dataset evaluation/qasper/qasper_test.json `
  --exclude-dataset evaluation/qasper_train/qasper_train_development.json `
  --exclude-dataset evaluation/qasper_train/qasper_train_heldout.json
```
