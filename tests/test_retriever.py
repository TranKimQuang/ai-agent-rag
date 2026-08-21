from app.models import Chunk
from app.rag.retriever import InMemoryBM25Retriever


def test_search_returns_relevant_chunk() -> None:
    retriever = InMemoryBM25Retriever()
    retriever.add(
        [
            Chunk(
                id="1",
                document_id="doc",
                filename="rag.pdf",
                page=1,
                text="BM25 is a keyword retrieval algorithm for search.",
            ),
            Chunk(
                id="2",
                document_id="doc",
                filename="rag.pdf",
                page=2,
                text="FastAPI is a Python web framework.",
            ),
            Chunk(
                id="3",
                document_id="doc",
                filename="rag.pdf",
                page=3,
                text="PostgreSQL stores application data.",
            ),
        ]
    )

    results = retriever.search("keyword retrieval")

    assert results[0].chunk_id == "1"
    assert results[0].page == 1


def test_empty_query_has_no_results() -> None:
    assert InMemoryBM25Retriever().search("anything") == []
