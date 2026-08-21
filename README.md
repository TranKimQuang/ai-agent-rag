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

## Checks

```powershell
ruff check .
pytest -q
```
