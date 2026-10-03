import pytest

from app.evaluation.significance import paired_bootstrap_comparison


def _row(question_id: str, method: str, retrieved: list[str]) -> dict[str, object]:
    return {
        "question_id": question_id,
        "method": method,
        "retrieved_chunk_ids": retrieved,
        "gold_chunk_ids": [f"gold-{question_id}"],
    }


def test_paired_bootstrap_detects_consistent_improvement() -> None:
    details = []
    for index in range(20):
        question_id = str(index)
        gold = f"gold-{question_id}"
        details.append(_row(question_id, "baseline", ["miss", gold]))
        details.append(_row(question_id, "candidate", [gold, "miss"]))

    report = paired_bootstrap_comparison(
        details,
        baseline_method="baseline",
        candidate_method="candidate",
        k=2,
        samples=500,
        seed=7,
    )

    mrr = report["metrics"]["mrr_at_k"]
    assert mrr["observed_difference"] == pytest.approx(0.5)
    assert mrr["confidence_interval"][0] > 0.0
    assert mrr["significant_at_0_05"] is True


def test_paired_bootstrap_requires_matching_questions() -> None:
    details = [
        _row("1", "baseline", ["gold-1"]),
        _row("2", "candidate", ["gold-2"]),
    ]

    with pytest.raises(ValueError, match="same questions"):
        paired_bootstrap_comparison(
            details,
            baseline_method="baseline",
            candidate_method="candidate",
            samples=10,
        )
