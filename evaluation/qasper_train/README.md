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

Regenerate with:

```powershell
python -m scripts.prepare_qasper_parquet_subset `
  --input output/qasper-train-raw/qasper/train/0000.parquet `
  --output-dir evaluation/qasper_train `
  --exclude-dataset evaluation/qasper/qasper_validation.json `
  --exclude-dataset evaluation/qasper/qasper_test.json
```
