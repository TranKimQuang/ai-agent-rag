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

## Development baseline

The first semantic-linking ablation on all 78 development questions produced these `k=5`
results:

- BM25: Recall 0.2781, MRR 0.2026, nDCG 0.2059.
- Semantic: Recall 0.2379, MRR 0.1761, nDCG 0.1785.
- Hybrid: Recall 0.2991, MRR 0.2331, nDCG 0.2306.
- Hybrid + Ontology re-ranking: identical to Hybrid.
- Hybrid + Ontology expansion: Recall 0.2703, MRR 0.2274, nDCG 0.2144.

Coverage analysis found concepts in only 7/78 queries and an Ontology relation between query and
gold evidence for only 3/78 questions. Therefore the development result does not justify opening
held-out v3. Expansion remains disabled because it caused query drift. Compact reproducible
records are stored in `development_retrieval_results.json` and
`development_coverage_analysis.json`.

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
