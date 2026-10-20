from app.evaluation.hierarchical_concept_linking import (
    best_concept_matches,
    concept_match,
    score_hierarchical_predictions,
)
from app.ontology.service import OntologyService
from scripts.evaluate_hierarchical_concept_linking import evaluate_rows


def test_exact_concept_match_receives_full_credit() -> None:
    match = concept_match(
        OntologyService(), "QuestionAnswering", "QuestionAnswering"
    )

    assert match is not None
    assert match.credit == 1.0
    assert match.relation == "exact"


def test_direct_narrower_concept_receives_partial_credit() -> None:
    match = concept_match(
        OntologyService(), "MachineReadingComprehension", "QuestionAnswering"
    )

    assert match is not None
    assert match.credit == 0.5
    assert match.relation == "predicted_is_narrower"


def test_unrelated_concepts_receive_no_credit() -> None:
    assert (
        concept_match(OntologyService(), "WordEmbedding", "QuestionAnswering")
        is None
    )


def test_matching_is_one_to_one() -> None:
    matches = best_concept_matches(
        OntologyService(),
        {"NaturalLanguageProcessing"},
        {"SemanticRoleInduction", "TextSummarization"},
    )

    assert len(matches) == 1
    assert sum(match.credit for match in matches) == 0.5


def test_hierarchical_score_preserves_exact_metrics_and_adds_partial_credit() -> None:
    result = score_hierarchical_predictions(
        OntologyService(),
        [{"QuestionAnswering"}, {"WordEmbedding"}],
        [{"MachineReadingComprehension"}, {"WordEmbedding"}],
    )

    assert result["exact"]["f1"] == 0.5
    assert result["taxonomy_aware"]["f1"] == 0.75
    assert result["counts"]["taxonomy_credit"] == 1.5


def test_scoped_evaluation_excludes_predictions_outside_label_catalog() -> None:
    result = evaluate_rows(
        OntologyService(),
        [
            {
                "source_question_id": "q1",
                "text": "Which QA method?",
                "gold_concepts": ["QuestionAnswering"],
                "predicted": ["QuestionAnswering", "WordEmbedding"],
            }
        ],
        "predicted",
        {"QuestionAnswering"},
    )

    assert result["exact"]["precision"] == 1.0
    assert result["excluded_prediction_assignments"] == 1
