from pathlib import Path

import numpy as np
from rdflib import OWL, RDF, RDFS, XSD, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS

from app.models import Chunk, ConceptLinkingMethod
from app.ontology.service import QA, OntologyService, local_name

CSO = Namespace("https://cso.kmi.open.ac.uk/topics/")


class ConceptLinkingEncoder:
    """Deterministic semantic space for concept-linking tests."""

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            normalized = text.lower()
            if (
                "retrieval augmented generation" in normalized
                or "retrieves external evidence" in normalized
            ):
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


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


def test_selected_topics_are_mapped_to_cso_v35() -> None:
    graph = OntologyService().graph
    expected_mappings = {
        QA.InformationRetrieval: CSO.information_retrieval,
        QA.NaturalLanguageProcessing: CSO.natural_language_processing,
        QA.QuestionAnswering: CSO.question_answering,
        QA.RetrievalAugmentedGeneration: CSO.retrieval_augmented_generation,
        QA.SemanticSearch: CSO.semantic_search,
    }

    for local_concept, cso_concept in expected_mappings.items():
        assert (local_concept, SKOS.exactMatch, cso_concept) in graph

    ontology = QA.DocumentQAOntology
    assert (ontology, DCTERMS.source, URIRef("https://cso.kmi.open.ac.uk/")) in graph
    assert (
        ontology,
        DCTERMS.license,
        URIRef("https://creativecommons.org/licenses/by/4.0/"),
    ) in graph


def test_semantic_concept_linking_finds_paraphrase_missing_from_aliases() -> None:
    service = OntologyService(semantic_encoder=ConceptLinkingEncoder())
    paraphrase = "The system retrieves external evidence before producing answers."

    alias_links = service.link_concepts(paraphrase, ConceptLinkingMethod.ALIAS)
    semantic_links = service.link_concepts(
        paraphrase,
        ConceptLinkingMethod.SEMANTIC,
        threshold=0.8,
    )

    assert alias_links == []
    assert semantic_links[0].concept == "RetrievalAugmentedGeneration"
    assert semantic_links[0].source == ConceptLinkingMethod.SEMANTIC
    assert semantic_links[0].score == 1.0


def test_hybrid_concept_linking_keeps_exact_alias_as_strongest_signal() -> None:
    service = OntologyService(semantic_encoder=ConceptLinkingEncoder())

    links = service.link_concepts(
        "RAG retrieves external evidence",
        ConceptLinkingMethod.HYBRID,
        threshold=0.8,
    )

    assert links[0].concept == "RetrievalAugmentedGeneration"
    assert links[0].source == ConceptLinkingMethod.ALIAS
    assert links[0].score == 1.0


def test_configured_hybrid_linking_is_used_when_indexing_chunks() -> None:
    service = OntologyService(
        semantic_encoder=ConceptLinkingEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.8,
    )

    chunks, link_count = service.index_chunks(
        [
            Chunk(
                id="semantic",
                document_id="doc",
                filename="paper.pdf",
                page=1,
                text="The system retrieves external evidence before producing answers.",
            )
        ]
    )

    assert chunks[0].concepts == ["RetrievalAugmentedGeneration"]
    assert link_count == 1
    assert service.is_chunk_indexed("semantic") is True
    assert service.is_chunk_indexed("missing") is False


def test_configured_concept_linking_caches_repeated_text() -> None:
    class CountingEncoder(ConceptLinkingEncoder):
        def __init__(self) -> None:
            self.calls = 0

        def encode(self, texts: list[str]) -> np.ndarray:
            self.calls += 1
            return super().encode(texts)

    encoder = CountingEncoder()
    service = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.8,
    )
    text = "The system retrieves external evidence before producing answers."

    first = service.configured_concepts(text)
    second = service.configured_concepts(text)

    assert first == second
    assert encoder.calls == 2  # one concept batch plus one unique input text


def test_prelinked_concepts_can_be_scored_without_encoding_text_again() -> None:
    match = OntologyService().score_concept_names(
        ["InformationRetrieval"],
        ["RetrievalAugmentedGeneration"],
    )

    assert match.score == 0.65
    assert match.query_concepts == ["InformationRetrieval"]
    assert match.chunk_concepts == ["RetrievalAugmentedGeneration"]


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


def test_validation_driven_vocabulary_links_real_research_phrases() -> None:
    service = OntologyService()

    concepts = {
        link.concept
        for link in service.link_concepts(
            "We compare RNN word embeddings using ROUGE for text summarization.",
            ConceptLinkingMethod.ALIAS,
        )
    }

    assert {
        "ROUGE",
        "RecurrentNeuralNetwork",
        "TextSummarization",
        "WordEmbedding",
    } <= concepts


def test_validation_driven_query_expansion_uses_domain_relations() -> None:
    expansion = OntologyService().expand_query(
        "How is semantic role induction evaluated on a parallel corpus?"
    )

    assert expansion.query_concepts == ["ParallelCorpus", "SemanticRoleInduction"]
    assert "natural language processing" in expansion.expansion_terms


def test_train_development_vocabulary_links_repeated_research_topics() -> None:
    service = OntologyService()

    concepts = {
        local_name(concept)
        for concept in service.identify_concepts(
            "The DMN uses word2vec before grammatical error correction."
        )
    }

    assert concepts == {
        "DynamicMemoryNetwork",
        "GrammaticalErrorCorrection",
        "Word2Vec",
    }


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
