# Local LLM smoke test — 26/09/2026

## End-to-end QASPER development smoke — 27/09/2026

Added `scripts/smoke_qasper_agent.py` to pass real QASPER development text
through retrieval, Ontology, the evidence gate, Qwen3:4b and server-owned
citations. The script refuses held-out input and can compare all six retrieval
variants without calling Ollama. It selects one question per distinct paper so
the five-case smoke is not dominated by one paper.

The first unscoped run found gold evidence for only 1/5 questions at top 5.
The Agent answered 4/5, but only one answer cited a gold chunk. Inspection found
that ambiguous paper-relative questions were retrieving plausible evidence
from other papers. `document_id` scoping was therefore added to the retrieval
stack, `/search`, `/ask`, and the Agent.

The scoped retrieval diagnostic at top 5 found 3/5 hits for BM25, 2/5 for
Semantic, 2/5 for Hybrid, 2/5 for Hybrid + Ontology re-ranking, and only 1/5
for each expansion variant. For the OpenIE question, expansion moved a gold
chunk from rank 1 to outside top 5 (rank 8/9 at top 10). This confirmed query
drift already observed on the larger development benchmark.

The Agent was also still calling expansion + re-ranking despite the documented
locked path being re-ranking-only. After correcting that inconsistency, the
same five scoped questions produced 2/5 retrieval hits, three answers and two
refusals; two answers cited gold chunks. The remaining answer cited a plausible
same-paper passage outside QASPER gold, showing that concept-driven evidence
acceptance still needs validation calibration. Mean end-to-end time was 15.322
seconds, including a 42.117-second first case. Final artifact:
`results/qasper_agent_smoke_20260926T170515Z.json`.

This tiny development smoke is diagnostic only. Gold citation overlap does not
prove answer correctness, and a non-gold citation is not automatically false.
No held-out evaluation was run or used to change configuration. Ruff and all
75 tests passed; the remaining warning is the existing Starlette/httpx
deprecation warning.

## GPU follow-up after NVIDIA driver update

The NVIDIA notebook driver was updated from 457.34 to 617.14 and Windows was
restarted. Ollama 0.34.4 then detected CUDA 13.4, a GTX 1650 (compute 7.5),
and 4 GB VRAM. Vulkan discovery timed out, but the CUDA backend succeeded.
Qwen3:4b offloaded 26/37 layers and Ollama reported 67% GPU / 33% CPU, using
about 2.3 GB VRAM. The first cold request took 82.964 seconds because discovery,
model loading and cache setup dominated it. A second warm 8-token request took
0.692 seconds and reported 22.51 generated tokens/second.

The Vietnamese four-case smoke was rerun while the model was warm and saved as
results/local_llm_vi_20260926T164438Z.json. The outcomes stayed 3/3 supported
answers and 1/1 evidence refusal. Times were 5.797, 6.548, 6.671 and 2.428
seconds, mean 5.361 seconds. This is about 2.92x faster than the earlier CPU
run's 15.650-second mean for the same four prompts. It is a single synthetic
development comparison, not a general performance claim or QASPER evaluation.

## Vietnamese multi-source development check

Artifact: results/local_llm_vi_20260926T162132Z.json, qwen3:4b on CPU.
Three synthetic evidence chunks were supplied directly to the generator.
On assistant inspection, 3/3 answerable questions had supported answers and
1/1 unanswerable question was refused. The BM25/Semantic comparison correctly
cited two different sources. Other cases covered 20 papers/75 questions,
RAM persistence/OCR, and refusal to invent an accuracy percentage.
Times: 20.809, 17.502, 17.910, 6.379 seconds; mean 15.650 seconds.
This is not independent human scoring, a retrieval/evidence-gate test, or a
QASPER benchmark. No held-out configuration was changed. The first attempt
failed while printing Vietnamese through Windows cp1252; console output now
uses JSON Unicode escapes, while the saved JSON preserves UTF-8 Vietnamese.

## Follow-up: server-owned sentence references

Implemented request-local sentence IDs and server-side quote reconstruction.
The model no longer writes quotes or document metadata. Unknown references
raise a generation error rather than being collapsed into evidence refusal.
Source-ID integrity still does not establish semantic entailment.

Rerun saved separately: results/local_llm_sentence_ids_20260926T161317Z.json.
All seven answerable cases returned supported answers on assistant inspection;
all three unanswerable cases were refused. The paper-count answer includes an
unnecessary additional fact about question count. No independent human scoring.
Times in question order: 13.301, 8.536, 8.986, 13.665, 9.139, 13.451, 11.276,
8.036, 5.910, 6.321 seconds. Mean 9.862 seconds. Single-run latency comparison
is confounded by cache, output length and simultaneous test workload.
73 tests passed; Ruff passed. Existing httpx/Starlette warning remains.
The original results and diagnosis below are retained as historical evidence.

## Setup

- Ollama 0.34.4; qwen3:4b, digest prefix 359d7dd4bcda.
- Windows, approximately 16 GB RAM; GTX 1650 4 GB, driver unchanged.
- Observed runtime: 100% CPU, context 4096, Ollama model size in memory 3.2 GB.
  This is not a measured peak working set or total system RAM.
- Temperature 0, thinking disabled, output cap 700 tokens.
- Fixed synthetic evidence supplied directly to the generator; no retrieval,
  evidence gate, PDF processing, or QASPER held-out involved in this run.
- Raw output: results/local_llm_smoke.json (results directory is gitignored).

## Observations

| Question topic | Expected answerable | Returned answer | Seconds |
|---|---|---|---:|
| BM25 | yes | yes, includes unnecessary semantic/hybrid details | 30.098 |
| Semantic search | yes | yes, includes unnecessary BM25/hybrid details | 30.708 |
| Hybrid search | yes | yes | 13.227 |
| Paper count (20) | yes | no | 24.019 |
| Question count (75) | yes | no | 9.883 |
| RAM after restart | yes | yes | 10.793 |
| Scanned PDFs | yes | yes | 9.250 |
| Accuracy (absent) | no | no | 4.319 |
| Authors (absent) | no | no | 4.133 |
| Gold price (absent) | no | no | 3.778 |

Mean wall time: 14.021 seconds/question; range 3.778–30.708 seconds.
The first case includes cold-start effects; subsequent cases still vary.

Assistant inspection found the five returned answers and their quotes supported
by the supplied text, but two answers include irrelevant extra information.
This is NOT an independent human evaluation. Human scoring fields remain null.
Five of seven answerable cases returned an answer; all three unanswerable cases
were refused by the pipeline. Do not interpret this tiny run as 80% general QA
accuracy or as proof of hallucination prevention.

The two false refusals may originate in the model or in strict quote validation.
The current adapter collapses invalid source quotes into refusal; raw model
output and rejection reason were not retained, so this run cannot distinguish
these causes. Do not attribute both refusals to model knowledge or retrieval.

## Next

Diagnostic rerun on 26/09 (unchanged prompt and validator): both count answers
were correct (20 papers / 75 questions) and answerable=true. Both generated a
non-verbatim quote: `The experiment used 2: 20 papers and 75 questions.`
The evidence actually says `The experiment used 20 papers and 75 questions.`
The validator correctly rejected the inserted `2: `. The adapter converted
this citation failure into a refusal, hiding the distinction from model refusal.
Durations: 21.756 and 8.086 seconds. Raw requests and responses are preserved in
results/local_llm_diagnostic_20260926T160840Z.json. Original smoke results unchanged.
This reproduces the failure but cannot recover the unrecorded first-run output.

Proposed fix: model selects server-assigned sentence IDs; server retrieves exact
quotes. Valid IDs alone still do not establish semantic support for a claim.
No production behavior or validation rules changed during diagnosis.

1. Preserve this first-run summary; add raw-output/rejection-reason diagnostics.
2. Investigate the two count questions without changing retrieval held-out.
3. Add Vietnamese, multiple-source and adversarial-evidence development cases.
4. Only then evaluate end-to-end /ask with real documents and human citation review.
5. CPU execution works but is slow; GPU acceleration has not been validated.
