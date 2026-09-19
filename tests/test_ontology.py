from pathlib import Path

from rdflib import OWL, RDF, RDFS, XSD, Literal

from app.models import Chunk
from app.ontology.service import QA, OntologyService


def test_ontology_has_core_schema_and_sample_individuals() -> None:
    service = OntologyService()

    summary = service.summary()

    assert summary.classes >= 13
    assert summary.object_properties >= 25
    assert summary.data_properties >= 9
    assert summary.individuals >= 13


def test_ontology_v2_models_authorship_citations_and_results() -> None:
    graph = OntologyService().graph

    assert (QA.SamplePaper, QA.hasAuthor, QA.SampleAuthor) in graph
    assert (QA.SamplePaper, QA.hasCitation, QA.SampleCitation) in graph
    assert (QA.SampleCitation, QA.citesPaper, QA.CitedPaper) in graph
    assert (QA.SamplePaper, QA.hasResult, QA.SampleResult) in graph
    assert (
        QA.SampleResult,
        QA.resultUsesMethod,
        QA.RetrievalAugmentedGeneration,
    ) in graph
    assert (QA.SampleResult, QA.resultUsesModel, QA.SampleRAGModel) in graph
    assert (QA.SampleResult, QA.resultUsesDataset, QA.QASPER) in graph
    assert (QA.SampleResult, QA.measuredBy, QA.EvidenceF1) in graph
    assert (
        QA.SampleResult,
        QA.metricValue,
        Literal("0.72", datatype=XSD.decimal),
    ) in graph


def test_ontology_v2_defines_inverse_properties_and_constraints() -> None:
    graph = OntologyService().graph

    assert (QA.hasAuthor, OWL.inverseOf, QA.authorOf) in graph
    assert (QA.hasCitation, OWL.inverseOf, QA.citationOf) in graph
    assert (QA.hasResult, OWL.inverseOf, QA.resultOf) in graph
    assert (QA.hasEvidence, OWL.inverseOf, QA.isEvidenceFor) in graph
    assert (QA.resultUsesDataset, RDFS.domain, QA.Result) in graph
    assert (QA.resultUsesDataset, RDFS.range, QA.Dataset) in graph
    assert (QA.metricValue, RDFS.domain, QA.Result) in graph
    assert (QA.metricValue, RDFS.range, XSD.decimal) in graph


def test_find_relations_answers_sample_competency_question() -> None:
    service = OntologyService()

    relations = service.find_relations("QASPER")

    assert any(
        relation.subject == "SamplePaper"
        and relation.predicate == "usesDataset"
        and relation.object == "QASPER"
        for relation in relations
    )


def test_unknown_concept_has_no_relations() -> None:
    assert OntologyService().find_relations("not-in-the-ontology") == []


def test_query_expansion_uses_alias_and_related_concept() -> None:
    expansion = OntologyService().expand_query("Tài liệu nói gì về hỏi đáp?")

    assert expansion.query_concepts == ["QuestionAnswering"]
    assert "QASPER" in expansion.expansion_terms
    assert "natural language processing" in expansion.expansion_terms


def test_ontology_scores_directly_related_concepts() -> None:
    match = OntologyService().score_text(
        "Nghiên cứu về information retrieval",
        "The proposed RAG pipeline retrieves evidence before answering.",
    )

    assert match.query_concepts == ["InformationRetrieval"]
    assert match.chunk_concepts == ["RetrievalAugmentedGeneration"]
    assert match.score == 0.65
    assert "Related concepts" in match.explanation


def test_example_sparql_queries_are_valid() -> None:
    service = OntologyService()
    query_directory = Path(__file__).parents[1] / "ontology" / "queries"

    results = [
        list(service.graph.query(path.read_text(encoding="utf-8")))
        for path in query_directory.glob("*.rq")
    ]

    assert len(results) == 5
    assert all(result for result in results)


def test_index_chunks_creates_knowledge_graph_links() -> None:
    service = OntologyService()
    chunks, link_count = service.index_chunks(
        [
            Chunk(
                id="doc:p1:c1",
                document_id="doc",
                filename="paper.pdf",
                page=1,
                text="RAG combines information retrieval with answer generation.",
            )
        ]
    )

    assert "RetrievalAugmentedGeneration" in chunks[0].concepts
    assert link_count >= 2
    chunk_resource = QA["chunk-doc:p1:c1"]
    assert (chunk_resource, RDF.type, QA.Chunk) in service.graph
    assert (chunk_resource, QA.mentionsConcept, QA.RetrievalAugmentedGeneration) in service.graph


def test_custom_ontology_path_can_be_loaded(tmp_path: Path) -> None:
    ontology_path = tmp_path / "tiny.ttl"
    ontology_path.write_text(
        """
        @prefix ex: <https://example.org/test#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ex:Concept a owl:Class .
        ex:item a ex:Concept .
        """,
        encoding="utf-8",
    )

    assert OntologyService(ontology_path).summary().individuals == 1
