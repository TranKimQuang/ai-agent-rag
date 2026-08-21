import pytest

from app.rag.chunking import chunk_pages, normalize_text


def test_normalize_text() -> None:
    assert normalize_text("AI\n  Agent\tRAG") == "AI Agent RAG"


def test_chunks_keep_page_metadata_and_overlap() -> None:
    chunks = chunk_pages(
        [(2, "one two three four five six")],
        document_id="doc-1",
        filename="guide.pdf",
        chunk_size=4,
        overlap=2,
    )

    assert [chunk.text for chunk in chunks] == ["one two three four", "three four five six"]
    assert all(chunk.page == 2 for chunk in chunks)


def test_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_pages([], document_id="doc", filename="x.pdf", chunk_size=10, overlap=10)

