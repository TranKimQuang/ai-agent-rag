import numpy as np

from app.evaluation.concept_linking import evaluate_concept_linking
from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService


class BenchmarkEncoder:
    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if (
                "retrieval augmented generation" in lowered
                or "external evidence" in lowered
                or "rag retrieves evidence" in lowered
            ):
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


def test_concept_linking_benchmark_compares_all_three_methods() -> None:
    service = OntologyService(semantic_encoder=BenchmarkEncoder())
    examples = [
        {
            "text": "RAG retrieves evidence",
            "gold_concepts": ["RetrievalAugmentedGeneration"],
        },
        {
            "text": "The system retrieves external evidence before producing answers.",
            "gold_concepts": ["RetrievalAugmentedGeneration"],
        },
        {
            "text": "A model retrieves external evidence to ground its generated response.",
            "gold_concepts": ["RetrievalAugmentedGeneration"],
        },
    ]

    results = evaluate_concept_linking(service, examples, threshold=0.8)

    assert set(results) == {method.value for method in ConceptLinkingMethod}
    assert results["semantic"]["recall"] > results["alias"]["recall"]
    assert results["hybrid"]["recall"] == 1.0
