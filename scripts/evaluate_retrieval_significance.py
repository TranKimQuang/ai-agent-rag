from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.benchmark import run_detailed_benchmark
from app.evaluation.significance import paired_bootstrap_comparison
from app.models import ConceptLinkingMethod, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder
from scripts.run_benchmark import load_dataset


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Paired bootstrap: Hybrid vs Ontology re-ranking",
        "",
        f"- Dataset: `{payload['dataset']}`",
        f"- Số câu hỏi: {payload['questions']}",
        f"- Cutoff: k={payload['k']}",
        f"- Bootstrap samples: {payload['bootstrap_samples']}",
        f"- Seed: {payload['seed']}",
        f"- Query type intent: {payload['query_type_intent']}",
        "",
        "| Metric | Hybrid | Ontology | Chênh lệch | 95% CI | p hai phía | Ý nghĩa 0,05 |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for name, metric in payload["metrics"].items():
        lower, upper = metric["confidence_interval"]
        significant = "Có" if metric["significant_at_0_05"] else "Không"
        lines.append(
            f"| {name} | {metric['baseline_mean']:.6f} | "
            f"{metric['candidate_mean']:.6f} | {metric['observed_difference']:+.6f} | "
            f"[{lower:+.6f}, {upper:+.6f}] | {metric['two_sided_p_value']:.4f} | "
            f"{significant} |"
        )
    lines.extend(
        [
            "",
            "## Diễn giải",
            "",
            (
                "Khoảng tin cậy chứa 0 nghĩa là chưa đủ bằng chứng để kết luận chênh lệch "
                "ổn định ở mức 0,05. Kết quả này chỉ áp dụng cho development split đã nêu; "
                "không được dùng để điều chỉnh theo held-out đã xem."
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Paired bootstrap for Hybrid and Ontology re-ranking."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper_train_v3/qasper_train_development.json"),
    )
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20261003)
    parser.add_argument(
        "--details",
        type=Path,
        help="Existing detailed benchmark JSON; skips model inference when provided.",
    )
    parser.add_argument(
        "--query-type-intent",
        action="store_true",
        help="Record that supplied details used the experimental query-type linker",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("evaluation/qasper_train_v3/development_significance.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("evaluation/qasper_train_v3/DEVELOPMENT_SIGNIFICANCE.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.details:
        details = json.loads(args.details.read_text(encoding="utf-8"))
        concept_links = None
        details_source = args.details.as_posix()
    else:
        chunks, questions = load_dataset(args.dataset)
        encoder = SentenceTransformerEncoder()
        ontology = OntologyService(
            semantic_encoder=encoder,
            linking_method=ConceptLinkingMethod.HYBRID,
            linking_threshold=0.65,
        )
        chunks, concept_links = ontology.index_chunks(chunks)
        retriever = InMemoryHybridRetriever(
            semantic_encoder=encoder,
            ontology_service=ontology,
            ontology_weight=0.05,
        )
        retriever.add(chunks)
        _, details = run_detailed_benchmark(
            retriever,
            questions,
            methods=[SearchMethod.HYBRID, SearchMethod.HYBRID_ONTOLOGY_RERANK],
            k_values=(args.k,),
        )
        details_source = "generated"
    report = paired_bootstrap_comparison(
        details,
        baseline_method=SearchMethod.HYBRID.value,
        candidate_method=SearchMethod.HYBRID_ONTOLOGY_RERANK.value,
        k=args.k,
        samples=args.samples,
        seed=args.seed,
    )
    payload = {
        "dataset": args.dataset.as_posix(),
        "split_role": "development",
        "details_source": details_source,
        "concept_links": concept_links,
        "linking_method": "hybrid",
        "linking_threshold": 0.65,
        "ontology_weight": 0.05,
        "query_type_intent": args.query_type_intent,
        **report,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
