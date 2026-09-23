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
    parser.add_argument("--threshold", type=float, default=0.40)
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
    results = evaluate_concept_linking(service, examples, threshold=args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
