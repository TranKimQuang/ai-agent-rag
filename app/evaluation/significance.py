from __future__ import annotations

from dataclasses import asdict

import numpy as np

from app.evaluation.benchmark import evaluate_ranking

METRIC_FIELDS = {
    "precision_at_k": "precision_at_k",
    "recall_at_k": "recall_at_k",
    "mrr_at_k": "reciprocal_rank",
    "ndcg_at_k": "ndcg_at_k",
}


def _metric_rows(
    details: list[dict[str, object]], method: str, *, k: int
) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    for row in details:
        if row["method"] != method:
            continue
        question_id = str(row["question_id"])
        metrics = evaluate_ranking(
            list(row["retrieved_chunk_ids"]),
            set(row["gold_chunk_ids"]),
            k=k,
        )
        raw_metrics = asdict(metrics)
        rows[question_id] = {
            output_name: float(raw_metrics[field_name])
            for output_name, field_name in METRIC_FIELDS.items()
        }
    return rows


def paired_bootstrap_comparison(
    details: list[dict[str, object]],
    *,
    baseline_method: str,
    candidate_method: str,
    k: int = 5,
    samples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 20261003,
) -> dict[str, object]:
    if samples <= 0:
        raise ValueError("Bootstrap samples must be greater than zero")
    if not 0.0 < confidence < 1.0:
        raise ValueError("Confidence must be between zero and one")

    baseline = _metric_rows(details, baseline_method, k=k)
    candidate = _metric_rows(details, candidate_method, k=k)
    if set(baseline) != set(candidate):
        raise ValueError("Baseline and candidate must contain the same questions")
    question_ids = sorted(baseline)
    if not question_ids:
        raise ValueError("No paired questions were found")

    rng = np.random.default_rng(seed)
    sampled_indices = rng.integers(
        0,
        len(question_ids),
        size=(samples, len(question_ids)),
    )
    alpha = 1.0 - confidence
    report: dict[str, object] = {}
    for metric in METRIC_FIELDS:
        baseline_values = np.asarray(
            [baseline[question_id][metric] for question_id in question_ids],
            dtype=np.float64,
        )
        candidate_values = np.asarray(
            [candidate[question_id][metric] for question_id in question_ids],
            dtype=np.float64,
        )
        paired_differences = candidate_values - baseline_values
        bootstrap_differences = paired_differences[sampled_indices].mean(axis=1)
        lower, upper = np.quantile(
            bootstrap_differences,
            [alpha / 2.0, 1.0 - alpha / 2.0],
        )
        non_positive = (np.count_nonzero(bootstrap_differences <= 0.0) + 1) / (
            samples + 1
        )
        non_negative = (np.count_nonzero(bootstrap_differences >= 0.0) + 1) / (
            samples + 1
        )
        report[metric] = {
            "baseline_mean": float(baseline_values.mean()),
            "candidate_mean": float(candidate_values.mean()),
            "observed_difference": float(paired_differences.mean()),
            "confidence_interval": [float(lower), float(upper)],
            "two_sided_p_value": float(min(1.0, 2.0 * min(non_positive, non_negative))),
            "improved_questions": int(np.count_nonzero(paired_differences > 0.0)),
            "unchanged_questions": int(np.count_nonzero(paired_differences == 0.0)),
            "worsened_questions": int(np.count_nonzero(paired_differences < 0.0)),
            "significant_at_0_05": bool(lower > 0.0 or upper < 0.0),
        }

    return {
        "baseline_method": baseline_method,
        "candidate_method": candidate_method,
        "questions": len(question_ids),
        "k": k,
        "bootstrap_samples": samples,
        "confidence": confidence,
        "seed": seed,
        "metrics": report,
    }
