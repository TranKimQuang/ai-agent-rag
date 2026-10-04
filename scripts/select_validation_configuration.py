import argparse
import json
from pathlib import Path
from typing import Any


def select_configuration(reports: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = []
    for report in reports:
        for weight, result in report["by_weight"].items():
            metrics = result["metrics"]["hybrid_ontology_rerank"]
            candidates.append(
                {
                    "query_type_intent": bool(report["query_type_intent"]),
                    "ontology_weight": float(weight),
                    "metrics": metrics,
                }
            )
    selected = max(
        candidates,
        key=lambda candidate: (
            candidate["metrics"]["ndcg@5"],
            candidate["metrics"]["mrr@5"],
            candidate["metrics"]["recall@5"],
            not candidate["query_type_intent"],
            -candidate["ontology_weight"],
        ),
    )
    baseline = reports[0]["baseline"]["hybrid"]
    expansion_candidates = [
        {
            "query_type_intent": bool(report["query_type_intent"]),
            "metrics": report["baseline"]["hybrid_ontology_expansion"],
        }
        for report in reports
    ]
    best_expansion = max(
        expansion_candidates,
        key=lambda candidate: (
            candidate["metrics"]["ndcg@5"],
            candidate["metrics"]["mrr@5"],
            candidate["metrics"]["recall@5"],
        ),
    )
    use_reranking = selected["ontology_weight"] > 0 and (
        selected["metrics"]["ndcg@5"] > baseline["ndcg@5"]
    )
    use_expansion = best_expansion["metrics"]["ndcg@5"] > baseline["ndcg@5"]
    return {
        "selection_split": "validation",
        "questions": reports[0]["questions"],
        "selection_metric": "nDCG@5, then MRR@5 and Recall@5",
        "selected": {
            "retrieval_method": "hybrid_ontology_rerank" if use_reranking else "hybrid",
            "query_type_intent": selected["query_type_intent"] if use_reranking else False,
            "ontology_weight": selected["ontology_weight"] if use_reranking else 0.0,
            "query_expansion": use_expansion,
        },
        "baseline_metrics": baseline,
        "best_rerank_candidate": selected,
        "best_expansion_candidate": best_expansion,
        "final_test_status": "sealed_not_evaluated",
        "decision": (
            "Validation did not show an nDCG@5 improvement from Ontology re-ranking "
            "or query expansion. Select the simpler Hybrid baseline and keep final-test sealed."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    baseline = payload["baseline_metrics"]
    rerank = payload["best_rerank_candidate"]
    expansion = payload["best_expansion_candidate"]
    selected = payload["selected"]
    return "\n".join(
        [
            "# Validation configuration selection",
            "",
            f"- Questions: **{payload['questions']}**",
            f"- Final-test status: **{payload['final_test_status']}**",
            f"- Selected retrieval method: **{selected['retrieval_method']}**",
            f"- Query type intent: **{selected['query_type_intent']}**",
            f"- Ontology weight: **{selected['ontology_weight']:.3f}**",
            f"- Query expansion: **{selected['query_expansion']}**",
            "",
            "| Configuration | Recall@5 | MRR@5 | nDCG@5 |",
            "|---|---:|---:|---:|",
            (
                f"| Hybrid baseline | {baseline['recall@5']:.6f} | "
                f"{baseline['mrr@5']:.6f} | {baseline['ndcg@5']:.6f} |"
            ),
            (
                f"| Best re-ranking candidate (weight "
                f"{rerank['ontology_weight']:.3f}, type-intent "
                f"{rerank['query_type_intent']}) | {rerank['metrics']['recall@5']:.6f} | "
                f"{rerank['metrics']['mrr@5']:.6f} | {rerank['metrics']['ndcg@5']:.6f} |"
            ),
            (
                f"| Best expansion candidate (type-intent "
                f"{expansion['query_type_intent']}) | "
                f"{expansion['metrics']['recall@5']:.6f} | "
                f"{expansion['metrics']['mrr@5']:.6f} | "
                f"{expansion['metrics']['ndcg@5']:.6f} |"
            ),
            "",
            payload["decision"],
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select and freeze a retrieval configuration from validation reports"
    )
    parser.add_argument("reports", type=Path, nargs="+")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()

    reports = [json.loads(path.read_text(encoding="utf-8")) for path in args.reports]
    payload = select_configuration(reports)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
