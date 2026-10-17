import numpy as np
import pytest

from scripts.evaluate_supervised_concept_linking import (
    predictions_at_threshold,
    supervised_oof_scores,
)


def test_supervised_oof_scores_are_paper_disjoint_and_aligned() -> None:
    examples = [
        {"text": "embedding one", "gold_concepts": ["WordEmbedding"]},
        {"text": "embedding two", "gold_concepts": ["WordEmbedding"]},
        {"text": "other one", "gold_concepts": []},
        {"text": "other two", "gold_concepts": []},
        {"text": "embedding three", "gold_concepts": ["WordEmbedding"]},
        {"text": "other three", "gold_concepts": []},
    ]
    embeddings = np.asarray(
        [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]],
        dtype=np.float32,
    )
    groups = ["p1", "p1", "p2", "p2", "p3", "p3"]

    scores, folds, trained = supervised_oof_scores(
        examples,
        embeddings,
        groups,
        ["WordEmbedding"],
        n_splits=3,
        minimum_train_positives=1,
    )

    assert scores.shape == (6, 1)
    assert len(set(folds)) == 3
    assert folds[0] == folds[1]
    assert folds[2] == folds[3]
    assert trained == {"WordEmbedding": 3}


def test_supervised_oof_scores_rejects_misaligned_inputs() -> None:
    with pytest.raises(ValueError, match="equal lengths"):
        supervised_oof_scores(
            [{"text": "one", "gold_concepts": []}],
            np.asarray([[1.0], [0.0]], dtype=np.float32),
            ["p1"],
            [],
        )


def test_predictions_keep_alias_and_add_supported_label() -> None:
    predictions = predictions_at_threshold(
        [{"WordEmbedding"}],
        np.asarray([[0.75, 0.20]], dtype=np.float32),
        ["NaturalLanguageProcessing", "SemanticSearch"],
        0.70,
    )

    assert predictions == [{"WordEmbedding", "NaturalLanguageProcessing"}]
