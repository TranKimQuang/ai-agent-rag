import numpy as np

from app.models import Chunk, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import (
    InMemoryBM25Retriever,
    InMemoryHybridRetriever,
    InMemorySemanticRetriever,
    tokenize,
)


class FakeEncoder:
    """Deterministic vectors keep tests fast and independent from model downloads."""

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if any(word in lowered for word in ("car", "vehicle", "automobile")):
                vectors.append([1.0, 0.0])
            elif any(word in lowered for word in ("python", "programming", "code")):
                vectors.append([0.0, 1.0])
            else:
                vectors.append([0.5, 0.5])
        array = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        return array / norms


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


def test_tokenize_matches_vietnamese_with_or_without_accents() -> None:
    assert tokenize("Thuật toán tìm tài liệu") == tokenize("thuat toan tim tai lieu")


def test_semantic_search_matches_different_wording() -> None:
    retriever = InMemorySemanticRetriever(FakeEncoder())
    retriever.add(
        [
            Chunk(
                id="car",
                document_id="doc",
                filename="guide.pdf",
                page=1,
                text="An automobile needs regular maintenance.",
            ),
            Chunk(
                id="python",
                document_id="doc",
                filename="guide.pdf",
                page=2,
                text="Python is useful for programming.",
            ),
        ]
    )

    results = retriever.search("How should I maintain my vehicle?")

    assert results[0].chunk_id == "car"
    assert results[0].method == SearchMethod.SEMANTIC


def test_semantic_search_caches_repeated_query_embedding() -> None:
    class CountingEncoder(FakeEncoder):
        def __init__(self) -> None:
            self.calls = 0

        def encode(self, texts: list[str]) -> np.ndarray:
            self.calls += 1
            return super().encode(texts)

    encoder = CountingEncoder()
    retriever = InMemorySemanticRetriever(encoder)
    retriever.add(
        [
            Chunk(
                id="car",
                document_id="doc",
                filename="guide.pdf",
                page=1,
                text="An automobile needs maintenance.",
            )
        ]
    )

    retriever.search("vehicle maintenance")
    retriever.search("vehicle maintenance")

    assert encoder.calls == 2  # one chunk batch plus one unique query


def test_hybrid_search_fuses_keyword_and_semantic_ranks() -> None:
    retriever = InMemoryHybridRetriever(semantic_encoder=FakeEncoder())
    retriever.add(
        [
            Chunk(
                id="car",
                document_id="doc",
                filename="guide.pdf",
                page=1,
                text="An automobile needs regular maintenance.",
            ),
            Chunk(
                id="python",
                document_id="doc",
                filename="guide.pdf",
                page=2,
                text="Python programming uses readable code.",
            ),
        ]
    )

    results = retriever.search("Python code", method=SearchMethod.HYBRID)

    assert results[0].chunk_id == "python"
    assert results[0].method == SearchMethod.HYBRID
    assert results[0].bm25_score is not None
    assert results[0].semantic_score is not None


def test_search_can_be_scoped_to_one_document() -> None:
    retriever = InMemoryHybridRetriever(semantic_encoder=FakeEncoder())
    retriever.add(
        [
            Chunk(
                id="paper-a:1",
                document_id="paper-a",
                filename="paper-a.pdf",
                page=1,
                text="Python code from the wrong paper.",
            ),
            Chunk(
                id="paper-b:1",
                document_id="paper-b",
                filename="paper-b.pdf",
                page=1,
                text="Python programming evidence from the selected paper.",
            ),
        ]
    )

    results = retriever.search(
        "Python code",
        method=SearchMethod.HYBRID,
        document_id="paper-b",
    )

    assert results
    assert {result.document_id for result in results} == {"paper-b"}


class OntologyRerankEncoder:
    """Ranks a distractor first so Ontology can demonstrate re-ranking."""

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "unrelated surface match" in lowered or lowered.startswith(
                "information retrieval"
            ):
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


def test_ontology_aware_search_expands_and_reranks() -> None:
    retriever = InMemoryHybridRetriever(
        semantic_encoder=OntologyRerankEncoder(),
        ontology_service=OntologyService(),
    )
    retriever.add(
        [
            Chunk(
                id="distractor",
                document_id="doc",
                filename="paper.pdf",
                page=1,
                text="An unrelated surface match used only by the fake encoder.",
            ),
            Chunk(
                id="rag",
                document_id="doc",
                filename="paper.pdf",
                page=2,
                text="RAG retrieves evidence before generating an answer.",
            ),
        ]
    )

    results = retriever.search(
        "information retrieval",
        method=SearchMethod.HYBRID_ONTOLOGY,
    )

    assert results[0].chunk_id == "rag"
    assert results[0].ontology_score == 0.65
    assert results[0].query_concepts == ["InformationRetrieval"]
    assert results[0].chunk_concepts == ["RetrievalAugmentedGeneration"]
    assert "retrieval augmented generation" in (results[0].expanded_query or "")


def test_ontology_ablation_separates_expansion_and_reranking() -> None:
    retriever = InMemoryHybridRetriever(
        semantic_encoder=OntologyRerankEncoder(),
        ontology_service=OntologyService(),
    )
    retriever.add(
        [
            Chunk(
                id="distractor",
                document_id="doc",
                filename="paper.pdf",
                page=1,
                text="An unrelated surface match used only by the fake encoder.",
            ),
            Chunk(
                id="rag",
                document_id="doc",
                filename="paper.pdf",
                page=2,
                text="RAG retrieves evidence before generating an answer.",
            ),
        ]
    )

    expansion_only = retriever.search(
        "information retrieval",
        method=SearchMethod.HYBRID_ONTOLOGY_EXPANSION,
    )
    rerank_only = retriever.search(
        "information retrieval",
        method=SearchMethod.HYBRID_ONTOLOGY_RERANK,
    )

    assert expansion_only[0].method == SearchMethod.HYBRID_ONTOLOGY_EXPANSION
    assert "retrieval augmented generation" in (expansion_only[0].expanded_query or "")
    assert expansion_only[0].ontology_score is None
    assert rerank_only[0].method == SearchMethod.HYBRID_ONTOLOGY_RERANK
    assert rerank_only[0].expanded_query is None
    assert rerank_only[0].ontology_score == 0.65
    assert rerank_only[0].chunk_id == "rag"


def test_ontology_reranking_without_concepts_preserves_hybrid_ranking(
    monkeypatch,
) -> None:
    ontology = OntologyService()
    retriever = InMemoryHybridRetriever(
        semantic_encoder=OntologyRerankEncoder(),
        ontology_service=ontology,
    )
    chunks, _ = ontology.index_chunks(
        [
            Chunk(
                id=f"chunk-{index}",
                document_id="doc",
                filename="paper.pdf",
                page=index,
                text=f"generic passage number {index}",
            )
            for index in range(1, 25)
        ]
    )
    retriever.add(chunks)

    hybrid = retriever.search("generic passage", limit=5, method=SearchMethod.HYBRID)
    monkeypatch.setattr(
        ontology,
        "score_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("indexed empty concepts must not be linked again")
        ),
    )
    reranked = retriever.search(
        "generic passage",
        limit=5,
        method=SearchMethod.HYBRID_ONTOLOGY_RERANK,
    )

    assert [result.chunk_id for result in reranked] == [
        result.chunk_id for result in hybrid
    ]
