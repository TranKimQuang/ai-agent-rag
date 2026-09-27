import numpy as np

from app.models import SearchMethod, SearchResult
from app.rag.reranker import SentenceTransformerCrossEncoderReranker


def result(chunk_id: str) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        document_id="paper",
        filename="paper.pdf",
        page=1,
        text=f"Passage {chunk_id}",
        method=SearchMethod.HYBRID_ONTOLOGY_RERANK,
        score=0.0,
    )


def test_cross_encoder_reranker_orders_candidates_without_loading_real_model() -> None:
    class FakeCrossEncoder:
        def predict(self, pairs, show_progress_bar):
            assert len(pairs) == 3
            assert show_progress_bar is False
            return np.asarray([0.1, 0.9, 0.4], dtype=np.float32)

    reranker = SentenceTransformerCrossEncoderReranker()
    reranker._model = FakeCrossEncoder()

    ranked = reranker.rerank("question", [result("a"), result("b"), result("c")])

    assert [item.chunk_id for item in ranked] == ["b", "c", "a"]
    assert ranked[0].score > ranked[1].score


def test_cross_encoder_reranker_accepts_empty_candidates() -> None:
    assert SentenceTransformerCrossEncoderReranker().rerank("question", []) == []
