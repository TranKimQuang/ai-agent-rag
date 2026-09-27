import pytest

from app.models import SearchMethod, SearchResult
from scripts.evaluate_cross_encoder_reranker import (
    find_gold_rank,
    reciprocal_rank,
    rerank_with_scores,
)


def result(chunk_id: str) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        document_id="paper",
        filename="paper.json",
        page=1,
        text="Evidence.",
        method=SearchMethod.HYBRID_ONTOLOGY_RERANK,
        score=0.0,
    )


def test_reranker_orders_candidates_by_cross_encoder_score() -> None:
    reranked = rerank_with_scores(
        [result("a"), result("b"), result("c")],
        [0.2, 0.9, 0.4],
    )

    assert [item.chunk_id for item in reranked] == ["b", "c", "a"]
    assert find_gold_rank(reranked, {"c"}) == 2


def test_reranker_rejects_mismatched_scores() -> None:
    with pytest.raises(ValueError, match="same length"):
        rerank_with_scores([result("a")], [])


def test_reciprocal_rank_handles_missing_result() -> None:
    assert reciprocal_rank(4) == 0.25
    assert reciprocal_rank(None) == 0.0
