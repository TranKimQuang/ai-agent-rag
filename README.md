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

The search endpoint supports three methods:

- `bm25`: exact keyword retrieval.
- `semantic`: meaning-based retrieval with multilingual sentence embeddings.
- `hybrid`: combines both rankings with Reciprocal Rank Fusion (default).

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

## Step 3: Ontology foundation

The first ontology version is stored in `ontology/document_qa.ttl`. It defines core AI/NLP
resources such as papers, chunks, research tasks, methods, datasets, and metrics. Sample
individuals and relations make the model executable before automatic extraction is added.

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

## Checks

```powershell
ruff check .
pytest -q
```
