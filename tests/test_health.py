from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ontology_summary() -> None:
    response = client.get("/ontology/summary")

    assert response.status_code == 200
    assert response.json()["classes"] >= 13


def test_ontology_concept_relations() -> None:
    response = client.get("/ontology/concepts/QASPER")

    assert response.status_code == 200
    assert response.json()["relations"][0]["object"] == "QASPER"


def test_unknown_ontology_concept_returns_404() -> None:
    response = client.get("/ontology/concepts/unknown")

    assert response.status_code == 404
