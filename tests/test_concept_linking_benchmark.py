import json
from pathlib import Path

import numpy as np
import pytest

from app.evaluation.concept_linking import (
    evaluate_concept_linking,
    evaluate_concept_linking_with_rows,
)
from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService
from scripts.run_concept_linking_benchmark import (
    load_examples,
    load_label_overrides,
    validate_gold_concepts,
)


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


def test_detailed_benchmark_retains_predictions_from_same_run() -> None:
    service = OntologyService(semantic_encoder=BenchmarkEncoder())
    examples = [
        {
            "source_question_id": "q1",
            "text": "RAG retrieves evidence",
            "gold_concepts": ["RetrievalAugmentedGeneration"],
        }
    ]

    details = evaluate_concept_linking_with_rows(service, examples, threshold=0.8)

    assert details["results"]["hybrid"]["f1"] == 1.0
    assert details["rows"][0]["source_question_id"] == "q1"
    assert details["rows"][0]["predictions"]["hybrid"]["concepts"] == [
        "RetrievalAugmentedGeneration"
    ]


def test_load_examples_merges_disjoint_review_batches(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        json.dumps(
            [
                {
                    "source_question_id": "q1",
                    "text": "First",
                    "gold_concepts": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps(
            [
                {
                    "source_question_id": "q2",
                    "text": "Second",
                    "gold_concepts": ["WordEmbedding"],
                }
            ]
        ),
        encoding="utf-8",
    )

    examples = load_examples([first, second])

    assert [item["text"] for item in examples] == ["First", "Second"]


def test_load_examples_rejects_duplicate_question_ids(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    row = {"source_question_id": "q1", "text": "Question", "gold_concepts": []}
    first.write_text(json.dumps([row]), encoding="utf-8")
    second.write_text(json.dumps([row]), encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate source_question_id: q1"):
        load_examples([first, second])


def test_load_examples_applies_audited_label_overrides(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.json"
    audit = tmp_path / "audit.json"
    dataset.write_text(
        json.dumps(
            [{"source_question_id": "q1", "text": "Question", "gold_concepts": []}]
        ),
        encoding="utf-8",
    )
    audit.write_text(
        json.dumps(
            {
                "corrections": [
                    {
                        "source_question_id": "q1",
                        "audited_concepts": ["NaturalLanguageProcessing"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    examples = load_examples([dataset], label_audits=[audit])

    assert examples[0]["gold_concepts"] == ["NaturalLanguageProcessing"]
    assert load_label_overrides([audit]) == {
        "q1": ["NaturalLanguageProcessing"]
    }


def test_load_examples_rejects_unused_label_override(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.json"
    audit = tmp_path / "audit.json"
    dataset.write_text(
        json.dumps(
            [{"source_question_id": "q1", "text": "Question", "gold_concepts": []}]
        ),
        encoding="utf-8",
    )
    audit.write_text(
        json.dumps(
            {
                "corrections": [
                    {"source_question_id": "q2", "audited_concepts": []}
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Label overrides do not match loaded examples"):
        load_examples([dataset], label_audits=[audit])


def test_validate_gold_concepts_rejects_disabled_concept() -> None:
    service = OntologyService()
    examples = [
        {
            "source_question_id": "q-disabled",
            "text": "Was the system evaluated by people?",
            "gold_concepts": ["HumanEvaluation"],
        }
    ]

    with pytest.raises(ValueError, match="HumanEvaluation"):
        validate_gold_concepts(service, examples)


def test_validate_gold_concepts_accepts_active_concept() -> None:
    service = OntologyService()
    examples = [
        {
            "source_question_id": "q-active",
            "text": "Does this use natural language processing?",
            "gold_concepts": ["NaturalLanguageProcessing"],
        }
    ]

    validate_gold_concepts(service, examples)
