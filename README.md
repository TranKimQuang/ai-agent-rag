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

## Checks

```powershell
ruff check .
pytest -q
```
