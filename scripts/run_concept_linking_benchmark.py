import argparse
import json
from pathlib import Path

from app.evaluation.concept_linking import ConceptLinkingExample, evaluate_concept_linking
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ontology concept-linking methods")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/concept_linking_sample.json"),
    )
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
        help="Semantic thresholds to compare on the validation labels.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/concept_linking_benchmark.json"),
    )
    args = parser.parse_args()

    examples: list[ConceptLinkingExample] = json.loads(
        args.dataset.read_text(encoding="utf-8")
    )
    service = OntologyService(semantic_encoder=SentenceTransformerEncoder())
    by_threshold = {
        f"{threshold:.2f}": evaluate_concept_linking(
            service,
            examples,
            threshold=threshold,
        )
        for threshold in sorted(set(args.thresholds))
    }
    selected_threshold = max(
        by_threshold,
        key=lambda threshold: (
            by_threshold[threshold]["hybrid"]["f1"],
            by_threshold[threshold]["hybrid"]["precision"],
            by_threshold[threshold]["semantic"]["f1"],
            -float(threshold),
        ),
    )
    results = {
        "selection_metric": "hybrid_f1",
        "selected_threshold": float(selected_threshold),
        "selected_results": by_threshold[selected_threshold],
        "by_threshold": by_threshold,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
