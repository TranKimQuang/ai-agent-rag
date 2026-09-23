# QASPER real-data subset

This directory contains a deterministic retrieval subset derived from the official QASPER v0.3
development split.

- Source: https://allenai.org/data/qasper
- Release archive: `qasper-train-dev-v0.3.tgz`
- Archive SHA-256: `a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a`
- License: CC BY 4.0
- Paper: Dasigi et al., *A Dataset of Information-Seeking Questions and Answers Anchored in
  Research Papers*, NAACL 2021.

## Split construction

Run:

```powershell
python -m scripts.prepare_qasper_subset `
  --input output/qasper-raw/qasper-dev-v0.3.json `
  --output-dir evaluation/qasper `
  --papers 20 `
  --validation-papers 10 `
  --min-questions-per-paper 3 `
  --max-questions-per-paper 5
```

Papers are sorted by identifier and selected deterministically. The first ten eligible papers
form validation and the next ten form test, so no paper appears in both splits. Only answerable
questions with textual evidence that maps exactly to a full-text paragraph are kept. Table and
figure evidence is excluded from this first retrieval experiment.

- Validation: 10 papers, 605 paragraph chunks, 42 questions.
- Test: 10 papers, 404 paragraph chunks, 33 questions.
- Total: 20 papers, 1,009 paragraph chunks, 75 questions.

The official JSON has no PDF page number. The `page` field therefore stores a one-based paragraph
ordinal solely to satisfy the current chunk schema; final citations must not present it as a PDF
page.

## Initial validation finding

The first ablation run found no difference between Hybrid and the three Ontology variants. Only
22 concept links were created across 605 validation chunks, so the current proof-of-concept
vocabulary has insufficient coverage of real QASPER papers. This is a diagnostic result, not a
final thesis score. The test split remains untouched until vocabulary expansion, concept-linking
validation, and Ontology-weight selection are complete.

The compact summary used for version control is stored in `validation_ablation_results.json`.
Full per-question output is generated locally under `results/qasper_validation/` and remains
ignored by Git because it is reproducible.

## Vocabulary expansion finding

The vocabulary was then extended using research concepts observed only in validation questions
and evidence, including argument mining, semantic-role induction, summarization evaluation,
spam detection, natural-language inference, recurrent neural networks, and word embeddings. The
held-out test split was not inspected or benchmarked during this iteration.

- Concept links increased from 22 to 171 across the same 605 validation chunks.
- Ontology re-ranking improved Recall@5 from 0.3016 to 0.3254 and MRR@5 from 0.2381 to 0.2560.
- Expansion alone slightly reduced MRR@5 to 0.2321, showing that adding related terms can also
  introduce query drift.
- The combined method reached Recall@5 0.3175 and MRR@5 0.2421; re-ranking alone was better on
  this validation set.

These remain validation results for vocabulary and weight development, not final test results.
The compact second-iteration summary is stored in `validation_vocabulary_results.json`.

## Concept-linking validation

Sixteen validation questions were manually labelled with applicable local concepts, including
one negative example. This small diagnostic set compares alias, semantic, and hybrid concept
linking without using the held-out test split. Thresholds from 0.35 through 0.60 were compared;
0.55 was selected by Hybrid F1, with Semantic F1 used to break ties.

At threshold 0.55, alias linking achieved F1 0.7143, semantic linking F1 0.7586, and hybrid
linking F1 0.9412. The labelled input and complete threshold sweep are stored in
`concept_linking_validation.json` and `concept_linking_validation_results.json`.
