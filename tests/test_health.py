from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_user_interface() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "OntoRAG Workspace" in response.text
    assert "/static/styles.css" in response.text


def test_ontology_summary() -> None:
    response = client.get("/ontology/summary")

    assert response.status_code == 200
    assert response.json()["classes"] >= 13


def test_ontology_concept_relations() -> None:
    response = client.get("/ontology/concepts/QASPER")

    assert response.status_code == 200
    assert any(
        relation["subject"] == "SamplePaper"
        and relation["predicate"] == "usesDataset"
        and relation["object"] == "QASPER"
        for relation in response.json()["relations"]
    )


def test_unknown_ontology_concept_returns_404() -> None:
    response = client.get("/ontology/concepts/unknown")

    assert response.status_code == 404


def test_ontology_query_expansion_api() -> None:
    response = client.get("/ontology/expand", params={"q": "hỏi đáp"})

    assert response.status_code == 200
    assert response.json()["query_concepts"] == ["QuestionAnswering"]
    assert "QASPER" in response.json()["expansion_terms"]


def test_alias_concept_linking_api() -> None:
    response = client.get(
        "/ontology/concept-linking",
        params={"q": "Hệ thống dùng RAG để hỏi đáp", "method": "alias"},
    )

    assert response.status_code == 200
    assert response.json()["method"] == "alias"
    assert any(
        link["concept"] == "RetrievalAugmentedGeneration" and link["source"] == "alias"
        for link in response.json()["links"]
    )
