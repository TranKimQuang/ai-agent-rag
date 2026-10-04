# QASPER protocol v4

This protocol excludes every paper used by the earlier QASPER protocols. Paper selection is deterministic and paper-disjoint.

- Development may be used for error analysis and method development.
- Validation may be used for selecting thresholds and configurations.
- Final test is sealed and has not been evaluated. Commit the frozen configuration before running it once.

See `protocol_manifest.json` for counts, SHA-256 hashes and the selection seed.

## Split summary

- Development: 20 papers, 1,019 chunks, 74 evidence-labelled questions.
- Validation: 10 papers, 402 chunks, 35 evidence-labelled questions.
- Final test: 15 papers, 662 chunks, 57 evidence-labelled questions; sealed and not evaluated.
- Excluded from selection: 100 unique papers used by earlier protocols.

## Initial development baseline

The current frozen retrieval implementation was evaluated only on development. At `k=5`:

- BM25: Recall 0.1919, MRR 0.1613, nDCG 0.1467.
- Semantic: Recall 0.3270, MRR 0.2358, nDCG 0.2400.
- Hybrid: Recall 0.3027, MRR 0.2074, nDCG 0.2113.
- Hybrid + Ontology re-ranking: Recall 0.3027, MRR 0.2092, nDCG 0.2128.
- Hybrid + query expansion: Recall 0.2892, MRR 0.2074, nDCG 0.2087.

Hybrid linking at threshold 0.65 linked concepts for 9/74 queries and 34/74 gold-evidence
sets; only 5/74 question/evidence pairs had a non-zero Ontology relation. Re-ranking changed
MRR for only one question and did not change Recall@5. Paired bootstrap over 10,000 samples
did not show a significant difference at 0.05. These results confirm that generalization and
concept coverage remain the next development problem; no validation or final-test result was
used.

## Development concept-candidate audit

All 65 development queries without an accepted concept were compared with the existing
ontology vocabulary below the production threshold. Only 3 were within 0.10 of the 0.65
threshold, 27 had a weak existing-vocabulary match and 35 were generic questions or likely
vocabulary gaps. Therefore, globally lowering the threshold is not supported by this audit.

The audit also found that the illustrative `SampleRAGModel` instance was being treated as a
linkable vocabulary concept. It has been excluded from concept linking. Re-running the full
development benchmark produced the same metrics and 370 accepted chunk links, so the bug did
not alter the reported baseline. See `DEVELOPMENT_CONCEPT_CANDIDATES.md`,
`development_concept_candidates.json` and `development_concept_review.csv`.

## Experimental query type intent

An opt-in query linker now recognizes explicit requests for a `Model`, `Dataset`, `Metric`,
`Method` or `Task`, and the re-ranker can match that class to concrete concepts in a chunk.
On development, query coverage increased from 9/74 to 42/74 and related query/evidence pairs
from 5/74 to 18/74. Re-ranking preserved Recall@5 at 0.3027 and increased MRR@5 from 0.2074
to 0.2110, but only 2/74 questions improved and the paired result was not significant
(`p=0.2704`). Expansion with these broad types reduced Recall@5 to 0.2757. The feature
therefore remains disabled by default and has not been selected on validation. Artifacts are
stored in `development_type_intent/`.

## External CSO candidate generation

The official CSO 3.5 CSV was downloaded from the CSO portal and recorded with SHA-256
`f8dda2793b63735fcc06e9bf6e8062f551c102efbcc1958079d3cf5c08f61d6b`. From 14,636
labelled topics, 1,901 topics below six relevant seeds (AI, NLP, IR, QA, Semantic Search and
Machine Learning) were used to generate candidates for the 32 still-uncovered development
queries. Fifteen top candidates scored at least 0.60, but a conservative semantic-plus-lexical
filter retained only `human evaluation`, `target language` and `machine translations`.

Activating these three concepts increased query coverage from 42/74 to 45/74 and accepted
chunk links from 370 to 406, but re-ranking MRR@5 decreased from 0.2110 to 0.2088. The CSO
mappings remain in the ontology with `retrievalEnabled=false`; they are excluded from active
linking and query expansion. The activated ablation remains available in
`development_cso_extension/`, while `development_cso_disabled/` verifies that disabled
candidates reproduce the earlier type-intent result.

## Validation selection

Validation evaluated query type intent both off and on across Ontology weights 0.00, 0.01,
0.025, 0.05, 0.075, 0.10, 0.15 and 0.20. The best re-ranking result tied the Hybrid baseline
only at weight 0.00; query expansion did not improve nDCG@5. The frozen validation decision is
therefore Hybrid without type intent, Ontology re-ranking or expansion. Final-test remains
sealed and unevaluated. See `VALIDATION_SELECTION.md` and `validation_selected_config.json`.
