# AI Agent + RAG

Starter project for building an AI Agent with Retrieval-Augmented Generation (RAG).

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to view the API documentation.

## Step 1: PDF retrieval

The first RAG pipeline stores its index in memory:

1. `POST /documents` extracts text from a PDF and splits each page into overlapping chunks.
2. The chunks are indexed with BM25 keyword retrieval.
3. `GET /search?q=...` returns matching chunks with their filename, page, and score.

Upload a PDF from PowerShell:

```powershell
$pdf = [System.IO.File]::ReadAllBytes("C:\path\to\document.pdf")
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/documents" `
  -Method Post `
  -ContentType "application/pdf" `
  -Headers @{ "X-Filename" = "document.pdf" } `
  -Body $pdf
```

Search the indexed document:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/search?q=keyword&limit=5"
```

The index is intentionally temporary at this stage and is cleared whenever the server restarts.

## Step 2: Semantic and hybrid retrieval

The search endpoint supports six methods:

- `bm25`: exact keyword retrieval.
- `semantic`: meaning-based retrieval with multilingual sentence embeddings.
- `hybrid`: combines both rankings with Reciprocal Rank Fusion (default).
- `hybrid_ontology_expansion`: Hybrid with Ontology query expansion only.
- `hybrid_ontology_rerank`: Hybrid with Ontology re-ranking only.
- `hybrid_ontology`: Hybrid with both query expansion and Ontology re-ranking.

The embedding model is loaded lazily on CPU when semantic or hybrid search is used for the first
time. The first request can therefore take longer while the model is downloaded and initialized.

```powershell
# Keyword search
Invoke-RestMethod "http://127.0.0.1:8000/search?q=BM25&method=bm25&limit=5"

# Meaning-based search
Invoke-RestMethod "http://127.0.0.1:8000/search?q=tim%20kiem%20theo%20y%20nghia&method=semantic&limit=5"

# Combined search (recommended)
Invoke-RestMethod "http://127.0.0.1:8000/search?q=tim%20kiem%20tai%20lieu&method=hybrid&limit=5"
```

## Step 3: Ontology foundation and v2 research model

The first ontology version is stored in `ontology/document_qa.ttl`. It defines core AI/NLP
resources such as papers, chunks, research tasks, methods, datasets, and metrics. Ontology v2
also models authorship, structured citations, and experiment results. A `Result` connects the
evaluated method/model, dataset, metric, numeric value, and supporting evidence instead of
attaching a metric directly to a paper. Inverse properties and explicit domain/range constraints
make these relations usable for inference and validation.

The API currently exposes read-only inspection endpoints:

```powershell
# Count classes, properties, and sample individuals
Invoke-RestMethod "http://127.0.0.1:8000/ontology/summary"

# Inspect incoming and outgoing relations for a named concept
Invoke-RestMethod "http://127.0.0.1:8000/ontology/concepts/QASPER" |
  ConvertTo-Json -Depth 5
```

This stage validates the knowledge model independently. The next stage will recognize ontology
concepts in document chunks and use those relations to expand and re-rank hybrid-search results.

## Step 4: Ontology-aware retrieval

The experimental `hybrid_ontology` method now connects the ontology to retrieval:

1. Recognize concepts and aliases in the question.
2. Expand the query with synonyms and directly related/broader/narrower concepts.
3. Run BM25 and semantic retrieval, then combine them with RRF.
4. Calculate an Ontology score from concepts found in each candidate chunk.
5. Re-rank candidates and return an explanation of the ontology signal.

```powershell
# Inspect query expansion without running retrieval
Invoke-RestMethod `
  "http://127.0.0.1:8000/ontology/expand?q=hoi%20dap" |
  ConvertTo-Json -Depth 5

# Run Hybrid + Ontology retrieval
Invoke-RestMethod `
  "http://127.0.0.1:8000/search?q=information%20retrieval&method=hybrid_ontology&limit=5" |
  ConvertTo-Json -Depth 5
```

The ontology schema is available in both Turtle (`ontology/document_qa.ttl`) and RDF/XML
(`ontology/document_qa.owl`). Example competency questions and SPARQL queries are stored in the
same directory. This remains a small proof of concept; the next step is to create concept links
from real PDF chunks and prepare a labelled evaluation set.

The project also maps a deliberately small subset of local topics to Computer Science Ontology
v3.5 resources with `skos:exactMatch`: Information Retrieval, Natural Language Processing,
Question Answering, Retrieval-Augmented Generation, and Semantic Search. Mapping decisions and
official sources are documented in `ontology/CSO_MAPPING.md`; the full CSO is not imported.

Concept linking can be inspected with three explicit strategies: `alias` (exact aliases),
`semantic` (embedding similarity), and `hybrid` (the union, with exact aliases taking priority):

```powershell
Invoke-RestMethod `
  "http://127.0.0.1:8000/ontology/concept-linking?q=retrieves%20external%20evidence%20before%20answering&method=semantic&threshold=0.40" |
  ConvertTo-Json -Depth 5
```

Run the development comparison with:

```powershell
python -m scripts.run_concept_linking_benchmark
```

This writes Precision, Recall, F1, and exact-match scores to
`results/concept_linking_benchmark.json`. The included six-example dataset is a pipeline fixture,
not final thesis evidence; it must later be replaced with manually labelled QASPER text.

## Step 5: Chunk concept indexing and benchmark

When a PDF is uploaded, detected concepts are now attached to each chunk and written into the
in-memory knowledge graph as `Chunk -> mentionsConcept -> Concept` triples. The ingest response
includes `concept_links`, which reports how many links were created.

The application and benchmark pipeline use hybrid concept linking: exact aliases remain the
strongest signal, while multilingual sentence embeddings can link paraphrases that do not appear
in the alias list. Chunk texts are encoded as one batch and share the same embedding encoder as
semantic retrieval. The current development configuration uses threshold `0.60`, re-ranking
weight `0.05`, and disables query expansion in the locked retrieval path because expansion caused
query drift.

A reproducible benchmark runner compares BM25 and Semantic retrieval plus the four ablation
configurations Hybrid, Hybrid + Expansion, Hybrid + Re-ranking, and Hybrid + both Ontology
components. It reports Precision@k, Recall@k, MRR, and nDCG@k:

```powershell
python -m scripts.run_benchmark --dataset evaluation/sample_benchmark.json --k-values 1 3 5
```

Summary results are written to `results/retrieval_benchmark.json` and
`results/retrieval_benchmark.csv`. The runner also creates a per-question result file and
`results/ontology_rank_changes.csv`, which directly compares the gold-evidence rank before and
after Ontology re-ranking. The included dataset is only a development fixture; do not use its
scores as final thesis evidence.

On the 72-question QASPER-train development split, semantic concept linking raised Ontology
re-ranking over plain Hybrid at `k=5`: Recall `0.2037 -> 0.2176`, MRR `0.1648 -> 0.1764`, and
nDCG `0.1576 -> 0.1697`. Expansion variants were worse and remain disabled. These are model
development results, not final held-out thesis results.

A deterministic real-data subset of official QASPER v0.3 is stored under `evaluation/qasper`.
It contains 20 papers and 75 evidence-labelled questions split by paper into validation and test.
See `evaluation/qasper/README.md` for provenance, checksum, limitations, and reproduction steps.

Generate the controlled sixteen-page PDF fixture and its twenty-four-question benchmark with:

```powershell
python -m scripts.create_benchmark_pdf
```

The PDF is saved to `output/pdf/tai-lieu-kiem-thu-ontology-rag.pdf`, and its labelled benchmark
is saved to `evaluation/pdf_benchmark.json`.

## Checks

```powershell
ruff check .
pytest -q
```

## Step 6: Agent orchestration and evidence gate

`POST /ask` now coordinates Ontology-aware retrieval, evidence validation, answer generation,
and citation validation. The first implementation intentionally uses a deterministic extractive
generator so the control flow can be tested without an API key or network call.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/ask" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"QA thuộc lĩnh vực NLP như thế nào?","limit":5}' |
  ConvertTo-Json -Depth 6
```

If evidence is weak, the Agent returns `insufficient_evidence` and does not call the answer
generator. The next iteration will replace the extractive generator with an LLM provider while
keeping the same evidence gate, citations, and orchestration trace.
