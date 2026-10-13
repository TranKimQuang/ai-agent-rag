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
    expected_exact_mappings = {
        QA.InformationRetrieval: CSO.information_retrieval,
        QA.NaturalLanguageProcessing: CSO.natural_language_processing,
    }
    expected_close_mappings = {
        QA.QuestionAnswering: CSO.question_answering,
        QA.RetrievalAugmentedGeneration: CSO["retrieval-augmented_generation"],
        QA.SemanticSearch: CSO.semantic_search,
    }

    for local_concept, cso_concept in expected_exact_mappings.items():
        assert (local_concept, SKOS.exactMatch, cso_concept) in graph
    for local_concept, cso_concept in expected_close_mappings.items():
        assert (local_concept, SKOS.closeMatch, cso_concept) in graph

    ontology = QA.DocumentQAOntology
    assert (ontology, DCTERMS.source, URIRef("https://cso.kmi.open.ac.uk/")) in graph
    assert (
        ontology,
        DCTERMS.license,
        URIRef("https://creativecommons.org/licenses/by/4.0/"),
    ) in graph


def test_conservative_development_candidates_are_mapped_to_cso() -> None:
    graph = OntologyService().graph
    expected = {
        QA.HumanEvaluation: CSO.human_evaluation,
        QA.TargetLanguage: CSO.target_language,
        QA.MachineTranslation: CSO.machine_translations,
    }

    for local_concept, cso_concept in expected.items():
        assert (local_concept, SKOS.exactMatch, cso_concept) in graph
        assert (
            local_concept,
            QA.retrievalEnabled,
            Literal(False, datatype=XSD.boolean),
        ) in graph


def test_disabled_cso_candidates_do_not_change_active_linker() -> None:
    service = OntologyService()

    linked = {
        local_name(concept)
        for concept in service.identify_concepts(
            "human evaluation of machine translation in the target language"
        )
    }

    assert linked.isdisjoint({"HumanEvaluation", "MachineTranslation", "TargetLanguage"})
    expansion = service.expand_query("neural machine translation")
    assert "machine translation" not in expansion.expansion_terms


def test_sample_instances_are_not_linkable_vocabulary_concepts() -> None:
    service = OntologyService()

    identified = {local_name(concept) for concept in service.identify_concepts("sample RAG model")}
    assert "RetrievalAugmentedGeneration" in identified
    assert "SampleRAGModel" not in identified
    assert all(
        candidate.concept != "SampleRAGModel"
        for candidate in OntologyService(
            semantic_encoder=ConceptLinkingEncoder()
        ).semantic_candidates("baseline model", limit=100)
    )


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


def test_semantic_candidates_are_returned_below_acceptance_threshold() -> None:
    service = OntologyService(semantic_encoder=ConceptLinkingEncoder())

    candidates = service.semantic_candidates("unrelated wording", limit=2)

    assert len(candidates) == 2
    assert candidates[0].source == ConceptLinkingMethod.SEMANTIC


def test_semantic_candidates_reject_invalid_limit() -> None:
    service = OntologyService(semantic_encoder=ConceptLinkingEncoder())

    try:
        service.semantic_candidates("text", limit=0)
    except ValueError as exc:
        assert str(exc) == "limit must be at least 1"
    else:
        raise AssertionError("Expected an invalid candidate limit to be rejected")


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


def test_query_and_chunk_linking_can_use_separate_thresholds() -> None:
    class ModerateConceptEncoder(ConceptLinkingEncoder):
        def encode(self, texts: list[str]) -> np.ndarray:
            vectors = []
            for text in texts:
                normalized = text.lower()
                if "before producing answers" in normalized:
                    vectors.append([0.9, 0.43589])
                elif "retrieval augmented generation" in normalized:
                    vectors.append([1.0, 0.0])
                else:
                    vectors.append([0.0, 1.0])
            return np.asarray(vectors, dtype=np.float32)

    service = OntologyService(
        semantic_encoder=ModerateConceptEncoder(),
        linking_method=ConceptLinkingMethod.SEMANTIC,
        linking_threshold=0.95,
        query_linking_threshold=0.80,
    )
    text = "The system retrieves external evidence before producing answers."

    assert service.configured_concepts(text) == []
    assert [
        local_name(concept) for concept in service.configured_query_concepts(text)
    ] == ["RetrievalAugmentedGeneration"]


def test_query_phrases_remove_question_scaffolding_and_keep_multiword_terms() -> None:
    phrases = OntologyService().query_phrases(
        "Which machine learning methods are used in experiments?"
    )

    assert phrases[0] == "which machine learning methods are used in experiments"
    assert "machine learning methods" in phrases
    assert "used experiments" not in phrases
    assert all(len(phrase.split()) > 1 for phrase in phrases[1:])


def test_phrase_linking_accepts_clear_phrase_candidate_and_rejects_ambiguous_one() -> None:
    class PhraseEncoder:
        def encode(self, texts: list[str]) -> np.ndarray:
            vectors = []
            for text in texts:
                normalized = text.lower()
                if (
                    "retrieve external evidence" in normalized
                    or "retrieval augmented generation" in normalized
                ):
                    vectors.append([1.0, 0.0, 0.0])
                elif "unclear wording" in normalized:
                    vectors.append([0.0, 0.71, 0.70])
                elif "question answering" in normalized:
                    vectors.append([0.0, 1.0, 0.0])
                else:
                    vectors.append([0.0, 0.0, 1.0])
            return np.asarray(vectors, dtype=np.float32)

    service = OntologyService(
        semantic_encoder=PhraseEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        query_phrase_linking=True,
        query_linking_threshold=0.55,
        query_phrase_margin=0.03,
    )

    clear = {
        local_name(concept)
        for concept in service.configured_query_concepts(
            "How does the system retrieve external evidence before answering?"
        )
    }
    ambiguous = service.link_query_concepts("What is unclear wording?")

    assert "RetrievalAugmentedGeneration" in clear
    assert all(link.score != 0.71 for link in ambiguous)


def test_phrase_linking_requires_stronger_semantic_score_after_exact_alias() -> None:
    class AnchoredPhraseEncoder:
        def encode(self, texts: list[str]) -> np.ndarray:
            vectors = []
            for text in texts:
                normalized = text.lower()
                if "semantic search" in normalized:
                    vectors.append([1.0, 0.0])
                elif "supervised learning" in normalized:
                    vectors.append([0.0, 1.0])
                elif "weak extra phrase" in normalized:
                    vectors.append([0.0, 0.56])
                else:
                    vectors.append([0.0, 0.0])
            return np.asarray(vectors, dtype=np.float32)

    service = OntologyService(
        semantic_encoder=AnchoredPhraseEncoder(),
        linking_method=ConceptLinkingMethod.HYBRID,
        query_phrase_linking=True,
        query_linking_threshold=0.55,
        query_phrase_margin=0.03,
    )

    links = service.link_query_concepts("semantic search with weak extra phrase")

    assert {link.concept for link in links} == {"SemanticSearch"}


def test_graph_chunk_candidates_follow_concepts_and_document_scope() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="rag-a",
                document_id="paper-a",
                filename="a.pdf",
                page=1,
                text="RAG retrieves evidence before answer generation.",
            ),
            Chunk(
                id="rag-b",
                document_id="paper-b",
                filename="b.pdf",
                page=1,
                text="RAG uses retrieved passages as evidence.",
            ),
        ]
    )

    candidates = service.graph_chunk_candidates(
        "information retrieval",
        document_id="paper-a",
    )

    assert [candidate.chunk_id for candidate in candidates] == ["rag-a"]
    assert candidates[0].score == 0.5
    assert candidates[0].query_concepts == ["InformationRetrieval"]
    assert candidates[0].matched_concepts == ["RetrievalAugmentedGeneration"]


def test_graph_chunk_candidates_require_query_concept() -> None:
    service = OntologyService()

    assert service.graph_chunk_candidates("completely unknown topic") == []


def test_prelinked_concepts_can_be_scored_without_encoding_text_again() -> None:
    match = OntologyService().score_concept_names(
        ["InformationRetrieval"],
        ["RetrievalAugmentedGeneration"],
    )

    assert match.score == 0.65
    assert match.query_concepts == ["InformationRetrieval"]
    assert match.chunk_concepts == ["RetrievalAugmentedGeneration"]


def test_query_type_intent_links_explicit_metric_request() -> None:
    service = OntologyService(query_type_intent=True)

    concepts = service.configured_query_concepts("What evaluation metrics were used?")

    assert QA.Metric in concepts


def test_query_type_intent_is_disabled_by_default() -> None:
    service = OntologyService()

    assert QA.Metric not in service.configured_query_concepts(
        "What evaluation metrics were used?"
    )


def test_query_type_scores_specific_concept_through_class_hierarchy() -> None:
    service = OntologyService(query_type_intent=True)

    metric_match = service.score_concept_names(["Metric"], ["ROUGE"])
    method_match = service.score_concept_names(["Method"], ["NeuralNetwork"])

    assert metric_match.score == 0.5
    assert method_match.score == 0.5
    assert "Requested type" in metric_match.explanation


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


def test_context_score_uses_question_type_and_explicit_passage_evidence() -> None:
    service = OntologyService()

    supported = service.score_context(
        "Which dataset is used for RAG?",
        "RAG is evaluated on the QASPER dataset.",
        query_concepts=["RetrievalAugmentedGeneration"],
        chunk_concepts=["RetrievalAugmentedGeneration", "QASPER"],
    )
    unsupported_type = service.score_context(
        "Which dataset is used for RAG?",
        "RAG retrieves evidence before answering.",
        query_concepts=["RetrievalAugmentedGeneration"],
        chunk_concepts=["RetrievalAugmentedGeneration"],
    )

    assert supported.score > unsupported_type.score
    assert "Dataset" in supported.query_concepts
    assert "passage contains QASPER" in supported.explanation


def test_context_score_does_not_bonus_unanchored_generic_entity_type() -> None:
    service = OntologyService()

    match = service.score_context(
        "Which model architecture do they use?",
        "The unrelated baseline uses a Transformer model.",
        query_concepts=[],
        chunk_concepts=["Transformer"],
    )

    assert match.score == 0.0
    assert "Question requests Model" in match.explanation


def test_context_score_downweights_semantic_only_and_hub_matches() -> None:
    service = OntologyService()

    explicit = service.score_context(
        "How is information retrieval performed?",
        "Information retrieval uses a lexical index.",
        query_concepts=["InformationRetrieval"],
        chunk_concepts=["InformationRetrieval"],
    )
    inferred = service.score_context(
        "How is the search performed?",
        "The system processes evidence.",
        query_concepts=["InformationRetrieval"],
        chunk_concepts=["InformationRetrieval"],
    )

    assert explicit.score > inferred.score
    assert 0.0 <= inferred.score <= 1.0


def test_example_sparql_queries_are_valid() -> None:
    service = OntologyService()
    query_directory = Path(__file__).parents[1] / "ontology" / "queries"

    results = [
        list(service.graph.query(path.read_text(encoding="utf-8")))
        for path in query_directory.glob("*.rq")
    ]

    assert len(results) == 10
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


def test_index_chunks_creates_paper_scoped_result_facts() -> None:
    service = OntologyService()
    chunks, _ = service.index_chunks(
        [
            Chunk(
                id="paper:p2:c1",
                document_id="paper",
                filename="paper.pdf",
                page=2,
                text="RAG achieved an Evidence F1 score of 72% on QASPER.",
            )
        ]
    )

    assert {
        "RetrievalAugmentedGeneration",
        "EvidenceF1",
        "QASPER",
    }.issubset(chunks[0].concepts)
    paper = QA["document-paper"]
    chunk = QA["chunk-paper:p2:c1"]
    result = QA["result-chunk-paper:p2:c1"]
    assert (paper, RDF.type, QA.Paper) in service.graph
    assert (paper, QA.hasResult, result) in service.graph
    assert (chunk, QA.isEvidenceFor, result) in service.graph
    assert (result, QA.resultUsesMethod, QA.RetrievalAugmentedGeneration) in service.graph
    assert (result, QA.resultUsesDataset, QA.QASPER) in service.graph
    assert (result, QA.measuredBy, QA.EvidenceF1) in service.graph
    assert (
        result,
        QA.metricValue,
        Literal("0.72", datatype=XSD.decimal),
    ) in service.graph


def test_result_context_scores_only_evidence_linked_to_a_result() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p2:result",
                document_id="paper",
                filename="paper.pdf",
                page=2,
                text="RAG achieved an Evidence F1 score of 72% on QASPER.",
            ),
            Chunk(
                id="paper:p1:overview",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text="This paper gives an overview of RAG and QASPER.",
            ),
        ]
    )

    result = service.score_context(
        "What result was achieved?",
        "RAG achieved an Evidence F1 score of 72% on QASPER.",
        query_concepts=[],
        chunk_concepts=["RetrievalAugmentedGeneration", "EvidenceF1", "QASPER"],
        chunk_id="paper:p2:result",
    )
    overview = service.score_context(
        "What result was achieved?",
        "This paper gives an overview of RAG and QASPER.",
        query_concepts=[],
        chunk_concepts=["RetrievalAugmentedGeneration", "QASPER"],
        chunk_id="paper:p1:overview",
    )

    assert result.score > overview.score
    assert "Paper-scoped Result context matched" in result.explanation


def test_result_context_extracts_paper_scoped_entities_without_global_vocabulary() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p3:c1",
                document_id="paper",
                filename="paper.pdf",
                page=3,
                text=(
                    "The ZXNet model achieved 83.5 BLEU on the FooBench dataset."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p3:c1"]
    datasets = list(service.graph.objects(result, QA.resultUsesDataset))
    metrics = list(service.graph.objects(result, QA.measuredBy))
    models = list(service.graph.objects(result, QA.resultUsesModel))
    assert [str(service.graph.value(value, SKOS.prefLabel)) for value in datasets] == [
        "FooBench"
    ]
    assert [str(service.graph.value(value, SKOS.prefLabel)) for value in metrics] == [
        "BLEU"
    ]
    assert [str(service.graph.value(value, SKOS.prefLabel)) for value in models] == [
        "ZXNet"
    ]
    assert (
        result,
        QA.metricValue,
        Literal("83.5", datatype=XSD.decimal),
    ) in service.graph
    assert "FooBench" not in service.vocabulary_labels()


def test_result_context_rejects_settings_and_related_work_sections() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:settings",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Settings. We compute BLEU on the FooBench dataset using the "
                    "ZXNet model."
                ),
            ),
            Chunk(
                id="paper:p2:related",
                document_id="paper",
                filename="paper.pdf",
                page=2,
                text=(
                    "Related Work. Prior ZXNet models achieved 90% accuracy on the "
                    "FooBench dataset."
                ),
            ),
        ]
    )

    assert (
        QA["document-paper"],
        QA.hasResult,
        QA["result-chunk-paper:p1:settings"],
    ) not in service.graph
    assert (
        QA["document-paper"],
        QA.hasResult,
        QA["result-chunk-paper:p2:related"],
    ) not in service.graph


def test_metric_values_only_use_sentences_that_name_a_metric() -> None:
    text = (
        "The corpus contains 3.2M words. "
        "The model achieved 74.40% accuracy. "
        "All runs used a length penalty of 1.0."
    )

    assert OntologyService._extract_metric_values(text) == ["0.744"]


def test_result_context_rejects_setup_roadmap_and_future_only_claims() -> None:
    service = OntologyService()
    chunks = [
        Chunk(
            id="paper:p1:system",
            document_id="paper",
            filename="paper.pdf",
            page=1,
            text="NER system. Prior work showed that NER obtained the best accuracy.",
        ),
        Chunk(
            id="paper:p2:baseline",
            document_id="paper",
            filename="paper.pdf",
            page=2,
            text="PBSMT Baseline. We optimize the language model to maximize BLEU.",
        ),
        Chunk(
            id="paper:p3:roadmap",
            document_id="paper",
            filename="paper.pdf",
            page=3,
            text=(
                "Introduction. Section 2 discusses the neural network and Section 3 "
                "presents the accuracy results."
            ),
        ),
        Chunk(
            id="paper:p4:future",
            document_id="paper",
            filename="paper.pdf",
            page=4,
            text=(
                "Conclusions. We believe the language model will improve accuracy and "
                "will conduct experiments in future work."
            ),
        ),
    ]
    service.index_chunks(chunks)

    paper = QA["document-paper"]
    assert not list(service.graph.objects(paper, QA.hasResult))


def test_result_context_rejects_experiment_setup_without_observed_outcome() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:experiment-setup",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Experiments. For the PBSMT task, we compare four baselines and "
                    "evaluate the systems using BLEU."
                ),
            )
        ]
    )

    assert not list(service.graph.objects(QA["document-paper"], QA.hasResult))


def test_result_context_rejects_numeric_experimental_setup() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:numeric-setup",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Experimental Setup. We report training accuracy on a validation "
                    "split containing 2,000 instances."
                ),
            )
        ]
    )

    assert not list(service.graph.objects(QA["document-paper"], QA.hasResult))


def test_result_context_rejects_prior_work_without_current_outcome() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:prior-work",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Audiovisual synchronisation. Previous approaches use the SyncNet "
                    "neural network. It achieves near perfect accuracy. We adopt the "
                    "original approach."
                ),
            )
        ]
    )

    assert not list(service.graph.objects(QA["document-paper"], QA.hasResult))


def test_result_context_keeps_current_result_after_prior_work_comparison() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:current-result",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Results. Previous approaches used a CNN. Our BERT model achieved "
                    "80% accuracy on the FooBench dataset."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:current-result"]
    assert (QA["document-paper"], QA.hasResult, result) in service.graph


def test_result_context_keeps_current_finding_with_future_work_and_one_role() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:conclusion",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Conclusion. In this work we studied a neural network and found "
                    "several useful resources. In the future we will study more languages."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:conclusion"]
    assert (QA["document-paper"], QA.hasResult, result) in service.graph


def test_result_context_keeps_explicit_current_result_with_one_typed_dimension() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:single-dimension",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Experiments. The results show that accuracy improved for French "
                    "and Portuguese."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:single-dimension"]
    assert (QA["document-paper"], QA.hasResult, result) in service.graph


def test_result_context_keeps_table_result_with_abbreviated_accuracy() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:table-result",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Data and Models. Table TABREF15 shows that the Multilingual Cased "
                    "model obtains 62.42% acc on DEV and 60.54% acc on TEST."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:table-result"]
    assert (QA["document-paper"], QA.hasResult, result) in service.graph


def test_result_context_rejects_cited_claim_without_current_result() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:cited-claim",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Word Embeddings. Neural network embeddings preserve regularities "
                    "BIBREF18 and help algorithms achieve better performance BIBREF4."
                ),
            )
        ]
    )

    assert not list(service.graph.objects(QA["document-paper"], QA.hasResult))


def test_result_context_rejects_hypothetical_gain_outside_result_section() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:hypothesis",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Multilingual. We believe that clustering features trained on the "
                    "Yelp dataset would be superior to those achieved out of domain."
                ),
            )
        ]
    )

    assert not list(service.graph.objects(QA["document-paper"], QA.hasResult))


def test_result_context_keeps_result_section_with_trailing_hypothesis() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:discussion",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Discussion and Error Analysis. The results confirm that our CRF "
                    "improves F1, but we believe data size explains one exception."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:discussion"]
    assert (QA["document-paper"], QA.hasResult, result) in service.graph


def test_paper_scoped_entities_filter_generic_datasets_and_role_noise() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p1:dataset-noise",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Results. If model size is not a constraint, our Faster-RCNN "
                    "approach achieved 80% accuracy on the Twitter dataset, a parallel "
                    "corpus benchmark, and the Moses BIBREF18 corpus."
                ),
            )
        ]
    )

    result = QA["result-chunk-paper:p1:dataset-noise"]
    model_labels = {
        str(service.graph.value(value, SKOS.prefLabel))
        for value in service.graph.objects(result, QA.resultUsesModel)
    }
    method_labels = {
        str(service.graph.value(value, SKOS.prefLabel))
        for value in service.graph.objects(result, QA.resultUsesMethod)
    }
    dataset_labels = {
        str(service.graph.value(value, SKOS.prefLabel))
        for value in service.graph.objects(result, QA.resultUsesDataset)
    }
    assert "Faster-RCNN" in model_labels
    assert "If" not in model_labels
    assert "Faster-RCNN" not in method_labels
    assert dataset_labels == set()


def test_model_architecture_named_as_approach_is_linked_as_model() -> None:
    service = OntologyService()
    service.index_chunks(
        [
            Chunk(
                id="paper:p5:c1",
                document_id="paper",
                filename="paper.pdf",
                page=5,
                text="Results. Our BLSTM approach achieved an F1 score of 0.48.",
            )
        ]
    )

    result = QA["result-chunk-paper:p5:c1"]
    model_labels = {
        str(service.graph.value(value, SKOS.prefLabel))
        for value in service.graph.objects(result, QA.resultUsesModel)
    }
    method_labels = {
        str(service.graph.value(value, SKOS.prefLabel))
        for value in service.graph.objects(result, QA.resultUsesMethod)
    }
    assert "BLSTM" in model_labels
    assert "BLSTM" not in method_labels


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
