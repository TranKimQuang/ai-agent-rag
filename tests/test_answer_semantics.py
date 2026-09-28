import numpy as np
import pytest

from scripts.evaluate_answer_semantics import (
    max_cosine_similarity,
    needs_manual_review,
)


def test_max_cosine_similarity_uses_best_reference() -> None:
    prediction = np.asarray([1.0, 0.0], dtype=np.float32)
    references = np.asarray([[0.0, 1.0], [0.8, 0.6]], dtype=np.float32)

    assert max_cosine_similarity(prediction, references) == pytest.approx(0.8)


def test_manual_review_flags_metric_disagreement_and_citation_mismatch() -> None:
    assert needs_manual_review(
        answer_f1=0.2,
        semantic_similarity=0.8,
        evidence_f1=1.0,
        status="answered",
    )
    assert needs_manual_review(
        answer_f1=0.8,
        semantic_similarity=0.8,
        evidence_f1=0.0,
        status="answered",
    )
    assert not needs_manual_review(
        answer_f1=0.8,
        semantic_similarity=0.9,
        evidence_f1=1.0,
        status="answered",
    )
