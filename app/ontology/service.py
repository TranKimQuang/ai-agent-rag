import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import SKOS

from app.models import (
    Chunk,
    ConceptLink,
    ConceptLinkingMethod,
    OntologyRelation,
    OntologySummary,
)

DEFAULT_ONTOLOGY_PATH = Path(__file__).parents[2] / "ontology" / "document_qa.ttl"
QA = Namespace("https://example.org/document-qa#")
_NON_WORD = re.compile(r"[^a-z0-9]+")


def normalize_text(text: str) -> str:
    lowered = text.lower().replace("đ", "d")
    without_accents = "".join(
        character
        for character in unicodedata.normalize("NFD", lowered)
        if unicodedata.category(character) != "Mn"
    )
    return " ".join(_NON_WORD.sub(" ", without_accents).split())


@dataclass(frozen=True)
class QueryExpansion:
    original_query: str
    expanded_query: str
    query_concepts: list[str]
    expansion_terms: list[str]


@dataclass(frozen=True)
class OntologyMatch:
    score: float
    query_concepts: list[str]
    chunk_concepts: list[str]
    explanation: str


class SemanticTextEncoder(Protocol):
    def encode(self, texts: list[str]) -> NDArray[np.float32]: ...


def local_name(value: URIRef) -> str:
    """Return the readable last component of an RDF URI."""
    text = str(value)
    return text.rsplit("#", maxsplit=1)[-1].rsplit("/", maxsplit=1)[-1]


class OntologyService:
    """Loads the small AI/NLP ontology and exposes read-only queries."""

    def __init__(
        self,
        ontology_path: Path = DEFAULT_ONTOLOGY_PATH,
        semantic_encoder: SemanticTextEncoder | None = None,
        linking_method: ConceptLinkingMethod = ConceptLinkingMethod.ALIAS,
        linking_threshold: float = 0.55,
        linking_limit: int = 5,
    ) -> None:
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
        self._semantic_encoder = semantic_encoder
        self.linking_method = linking_method
        self.linking_threshold = linking_threshold
        self.linking_limit = linking_limit
        self._concept_embeddings: NDArray[np.float32] | None = None
        self._concept_aliases = self._load_concept_aliases()

    def _load_concept_aliases(self) -> dict[URIRef, set[str]]:
        concept_types = {
            QA.Concept,
            QA.ResearchTopic,
            QA.Task,
            QA.Method,
            QA.Model,
            QA.Dataset,
            QA.Metric,
        }
        concepts = {
            subject
            for subject, object_type in self.graph.subject_objects(RDF.type)
            if object_type in concept_types and isinstance(subject, URIRef)
        }
        aliases: dict[URIRef, set[str]] = {}
        for concept in concepts:
            names = {local_name(concept)}
            for predicate in (RDFS.label, SKOS.prefLabel, SKOS.altLabel):
                names.update(str(value) for value in self.graph.objects(concept, predicate))
            aliases[concept] = {normalize_text(name) for name in names if normalize_text(name)}
        return aliases

    def identify_concepts(self, text: str) -> list[URIRef]:
        normalized = f" {normalize_text(text)} "
        matches = [
            concept
            for concept, aliases in self._concept_aliases.items()
            if any(f" {alias} " in normalized for alias in aliases)
        ]
        return sorted(matches, key=local_name)

    def _concept_documents(self) -> tuple[list[URIRef], list[str]]:
        concepts = sorted(self._concept_aliases, key=local_name)
        documents = []
        for concept in concepts:
            definitions = [str(value) for value in self.graph.objects(concept, SKOS.definition)]
            documents.append(
                " ".join(
                    [
                        self.preferred_label(concept),
                        local_name(concept),
                        *sorted(self._concept_aliases[concept]),
                        *definitions,
                    ]
                )
            )
        return concepts, documents

    def link_concepts(
        self,
        text: str,
        method: ConceptLinkingMethod = ConceptLinkingMethod.ALIAS,
        *,
        threshold: float = 0.55,
        limit: int = 5,
    ) -> list[ConceptLink]:
        """Link text to concepts with an explicit, comparable strategy."""
        return self.link_concepts_batch(
            [text], method, threshold=threshold, limit=limit
        )[0]

    def link_concepts_batch(
        self,
        texts: list[str],
        method: ConceptLinkingMethod = ConceptLinkingMethod.ALIAS,
        *,
        threshold: float = 0.55,
        limit: int = 5,
    ) -> list[list[ConceptLink]]:
        """Link a batch of texts while encoding semantic inputs only once."""
        links_by_text: list[dict[URIRef, ConceptLink]] = [{} for _ in texts]
        if method in {ConceptLinkingMethod.ALIAS, ConceptLinkingMethod.HYBRID}:
            for links, text in zip(links_by_text, texts, strict=True):
                for concept in self.identify_concepts(text):
                    links[concept] = ConceptLink(
                        concept=local_name(concept),
                        label=self.preferred_label(concept),
                        score=1.0,
                        source=ConceptLinkingMethod.ALIAS,
                    )

        if method in {ConceptLinkingMethod.SEMANTIC, ConceptLinkingMethod.HYBRID}:
            active = [index for index, text in enumerate(texts) if text.strip()]
            if self._semantic_encoder is not None and active:
                concepts, documents = self._concept_documents()
                if self._concept_embeddings is None:
                    self._concept_embeddings = self._semantic_encoder.encode(documents)
                text_vectors = self._semantic_encoder.encode([texts[index] for index in active])
                score_matrix = text_vectors @ self._concept_embeddings.T
                for row, text_index in enumerate(active):
                    links = links_by_text[text_index]
                    for concept_index in np.argsort(score_matrix[row])[::-1]:
                        score = min(
                            max(float(score_matrix[row, concept_index]), 0.0), 1.0
                        )
                        if score < threshold:
                            continue
                        concept = concepts[int(concept_index)]
                        if concept in links:
                            continue
                        links[concept] = ConceptLink(
                            concept=local_name(concept),
                            label=self.preferred_label(concept),
                            score=score,
                            source=ConceptLinkingMethod.SEMANTIC,
                        )

        return [
            sorted(links.values(), key=lambda link: (-link.score, link.concept))[:limit]
            for links in links_by_text
        ]

    def configured_concepts(self, text: str) -> list[URIRef]:
        """Link text using the strategy configured for the retrieval pipeline."""
        links = self.link_concepts(
            text,
            self.linking_method,
            threshold=self.linking_threshold,
            limit=self.linking_limit,
        )
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        return [known_by_name[link.concept] for link in links if link.concept in known_by_name]

    def configured_concepts_batch(self, texts: list[str]) -> list[list[URIRef]]:
        """Link configured concepts for many texts using one embedding batch."""
        linked = self.link_concepts_batch(
            texts,
            self.linking_method,
            threshold=self.linking_threshold,
            limit=self.linking_limit,
        )
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        return [
            [known_by_name[link.concept] for link in links if link.concept in known_by_name]
            for links in linked
        ]

    def index_chunks(self, chunks: list[Chunk]) -> tuple[list[Chunk], int]:
        """Annotate chunks and add document/page/chunk facts to the in-memory graph."""
        annotated: list[Chunk] = []
        concept_links = 0

        linked_chunks = self.configured_concepts_batch([chunk.text for chunk in chunks])
        for chunk, concepts in zip(chunks, linked_chunks, strict=True):
            document = URIRef(f"{QA}document-{chunk.document_id}")
            section = URIRef(f"{QA}section-{chunk.document_id}-page-{chunk.page}")
            chunk_resource = URIRef(f"{QA}chunk-{chunk.id}")
            self.graph.add((document, RDF.type, QA.Document))
            self.graph.add((document, QA.sourceFile, Literal(chunk.filename)))
            self.graph.add((document, QA.hasSection, section))
            self.graph.add((section, RDF.type, QA.Section))
            self.graph.add((section, QA.hasChunk, chunk_resource))
            self.graph.add((chunk_resource, RDF.type, QA.Chunk))
            self.graph.add(
                (chunk_resource, QA.pageNumber, Literal(chunk.page, datatype=XSD.integer))
            )
            self.graph.add((chunk_resource, QA.chunkText, Literal(chunk.text)))

            for concept in concepts:
                self.graph.add((chunk_resource, QA.mentionsConcept, concept))
                concept_links += 1

            annotated.append(
                chunk.model_copy(update={"concepts": [local_name(value) for value in concepts]})
            )

        return annotated, concept_links

    def _neighbors(self, concept: URIRef) -> set[URIRef]:
        predicates = {SKOS.broader, SKOS.narrower, SKOS.related, QA.relatedTo}
        neighbors: set[URIRef] = set()
        for predicate in predicates:
            neighbors.update(
                value
                for value in self.graph.objects(concept, predicate)
                if isinstance(value, URIRef)
            )
            neighbors.update(
                value
                for value in self.graph.subjects(predicate, concept)
                if isinstance(value, URIRef)
            )
        return neighbors

    def preferred_label(self, concept: URIRef) -> str:
        label = next(iter(self.graph.objects(concept, SKOS.prefLabel)), None)
        return str(label) if isinstance(label, Literal) else local_name(concept)

    def expand_query(self, query: str) -> QueryExpansion:
        concepts = self.configured_concepts(query)
        terms: set[str] = set()
        for concept in concepts:
            terms.update(str(value) for value in self.graph.objects(concept, SKOS.altLabel))
            terms.update(self.preferred_label(neighbor) for neighbor in self._neighbors(concept))

        normalized_query = normalize_text(query)
        useful_terms = sorted(
            term for term in terms if normalize_text(term) not in normalized_query
        )
        expanded_query = " ".join([query, *useful_terms]).strip()
        return QueryExpansion(
            original_query=query,
            expanded_query=expanded_query,
            query_concepts=[local_name(concept) for concept in concepts],
            expansion_terms=useful_terms,
        )

    def score_text(self, query: str, text: str) -> OntologyMatch:
        query_concepts = self.configured_concepts(query)
        chunk_concepts = self.configured_concepts(text)
        return self._score_concepts(query_concepts, chunk_concepts)

    def score_concept_names(
        self, query_concepts: list[str], chunk_concepts: list[str]
    ) -> OntologyMatch:
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        return self._score_concepts(
            [known_by_name[name] for name in query_concepts if name in known_by_name],
            [known_by_name[name] for name in chunk_concepts if name in known_by_name],
        )

    def _score_concepts(
        self, query_concepts: list[URIRef], chunk_concepts: list[URIRef]
    ) -> OntologyMatch:
        if not query_concepts or not chunk_concepts:
            return OntologyMatch(
                score=0.0,
                query_concepts=[local_name(value) for value in query_concepts],
                chunk_concepts=[local_name(value) for value in chunk_concepts],
                explanation="No ontology concept match was found.",
            )

        scores: list[float] = []
        reasons: list[str] = []
        for query_concept in query_concepts:
            best_score = 0.0
            for chunk_concept in chunk_concepts:
                if query_concept == chunk_concept:
                    best_score = 1.0
                    reasons.append(f"Exact concept: {local_name(query_concept)}")
                    break
                if chunk_concept in self._neighbors(query_concept):
                    best_score = max(best_score, 0.65)
                    reasons.append(
                        f"Related concepts: {local_name(query_concept)} -> "
                        f"{local_name(chunk_concept)}"
                    )
            scores.append(best_score)

        score = sum(scores) / len(scores)
        return OntologyMatch(
            score=score,
            query_concepts=[local_name(value) for value in query_concepts],
            chunk_concepts=[local_name(value) for value in chunk_concepts],
            explanation="; ".join(dict.fromkeys(reasons)) or "Concepts are not directly related.",
        )

    def summary(self) -> OntologySummary:
        classes = set(self.graph.subjects(RDF.type, OWL.Class))
        object_properties = set(self.graph.subjects(RDF.type, OWL.ObjectProperty))
        data_properties = set(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
        schema_resources = classes | object_properties | data_properties
        individuals = {
            subject
            for subject, object_type in self.graph.subject_objects(RDF.type)
            if object_type in classes and subject not in schema_resources
        }
        return OntologySummary(
            classes=len(classes),
            object_properties=len(object_properties),
            data_properties=len(data_properties),
            individuals=len(individuals),
        )

    def find_relations(self, concept: str) -> list[OntologyRelation]:
        """Find outgoing and incoming relations for one named resource."""
        wanted = concept.strip().casefold()
        resources = {
            value
            for value in set(self.graph.subjects()) | set(self.graph.objects())
            if isinstance(value, URIRef) and local_name(value).casefold() == wanted
        }
        if not resources:
            return []

        relations: set[tuple[str, str, str]] = set()
        for resource in resources:
            for subject, predicate, object_value in self.graph.triples((resource, None, None)):
                if isinstance(object_value, URIRef) and predicate != RDF.type:
                    relations.add(
                        (local_name(subject), local_name(predicate), local_name(object_value))
                    )
            for subject, predicate, object_value in self.graph.triples((None, None, resource)):
                if isinstance(subject, URIRef) and predicate != RDF.type:
                    relations.add(
                        (local_name(subject), local_name(predicate), local_name(object_value))
                    )

        return [
            OntologyRelation(subject=subject, predicate=predicate, object=object_value)
            for subject, predicate, object_value in sorted(relations)
        ]
