import pymupdf
from fastapi.testclient import TestClient

from app.main import app


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_ingest_and_search_pdf() -> None:
    client = TestClient(app)
    response = client.post(
        "/documents",
        content=make_pdf("BM25 finds relevant keyword passages in a RAG system."),
        headers={"content-type": "application/pdf", "x-filename": "rag-guide.pdf"},
    )

    assert response.status_code == 201
    assert response.json()["filename"] == "rag-guide.pdf"
    assert response.json()["pages"] == 1
    assert response.json()["chunks"] == 1

    search_response = client.get("/search", params={"q": "BM25 keyword"})
    assert search_response.status_code == 200
    assert search_response.json()["results"][0]["page"] == 1


def test_rejects_non_pdf_filename() -> None:
    response = TestClient(app).post(
        "/documents",
        content=b"not a PDF",
        headers={"content-type": "application/pdf", "x-filename": "notes.txt"},
    )

    assert response.status_code == 415
