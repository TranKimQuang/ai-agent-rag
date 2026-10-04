from scripts.select_validation_configuration import select_configuration


def report(type_intent: bool, candidate_ndcg: float, expansion_ndcg: float) -> dict:
    metrics = {
        "recall@5": 0.2,
        "mrr@5": 0.2,
        "ndcg@5": candidate_ndcg,
    }
    return {
        "questions": 10,
        "query_type_intent": type_intent,
        "baseline": {
            "hybrid": {"recall@5": 0.2, "mrr@5": 0.2, "ndcg@5": 0.2},
            "hybrid_ontology_expansion": {
                "recall@5": 0.2,
                "mrr@5": 0.2,
                "ndcg@5": expansion_ndcg,
            },
        },
        "by_weight": {
            "0.00": {"metrics": {"hybrid_ontology_rerank": metrics}},
        },
    }


def test_selection_prefers_simple_baseline_when_ontology_does_not_improve() -> None:
    selected = select_configuration(
        [report(False, 0.2, 0.2), report(True, 0.2, 0.15)]
    )

    assert selected["selected"] == {
        "retrieval_method": "hybrid",
        "query_type_intent": False,
        "ontology_weight": 0.0,
        "query_expansion": False,
    }
    assert selected["final_test_status"] == "sealed_not_evaluated"
