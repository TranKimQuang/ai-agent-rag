from rdflib import OWL, RDF, Graph, Namespace

from app.evaluation.ontology_quality import _consistency_issues, evaluate_ontology


def test_ontology_quality_report_passes_all_competency_questions() -> None:
    report = evaluate_ontology()

    assert report["consistent"] is True
    assert report["competency_questions_total"] == 10
    assert report["competency_questions_passed"] == 10
    assert report["triples_after_reasoning"] > report["triples_before_reasoning"]
    assert report["schema"]["classes"] >= 13
    assert report["cso_mapping"]["exact_match_count"] == 5
    assert report["cso_mapping"]["close_match_count"] == 3


def test_consistency_check_detects_disjoint_class_membership() -> None:
    example = Namespace("https://example.org/consistency-test#")
    graph = Graph()
    graph.add((example.Left, OWL.disjointWith, example.Right))
    graph.add((example.item, RDF.type, example.Left))
    graph.add((example.item, RDF.type, example.Right))

    issues = _consistency_issues(graph)

    assert len(issues) == 1
    assert issues[0].kind == "disjoint_class_membership"
    assert issues[0].resource == "item"
