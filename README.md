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

## Checks

```powershell
ruff check .
pytest -q
```
