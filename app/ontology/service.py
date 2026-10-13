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
_RESULT_OUTCOME_CUE = re.compile(
    r"\b(achieve|achieved|benefit|benefits|find|finds|found|gain|gains|higher|lower|"
    r"outperform|outperformed|outperforms|improve|improved|improves|show|shows|"
    r"shown)\b",
    re.IGNORECASE,
)
_RESULT_SECTION_CUE = re.compile(
    r"^(?:results?\b|experimental results?\b|validation\b|"
    r"conclusions?\b|discussion and conclusions?\b|dataset analysis\b|"
    r"discussion and error analysis\b|submitted systems?\b)",
    re.IGNORECASE,
)
_NON_RESULT_SECTION_CUE = re.compile(
    r"^(?:related works?\b|settings\b|method(?:s)?\b|error-analysis method\b|"
    r".*(?:methodology|experimental settings|experimental setup)\b|"
    r".*training details\b|"
    r"[^.\n]{1,60}\s+system\.|[^.\n]{1,60}\s+baseline\.)",
    re.IGNORECASE,
)
_PRIOR_WORK_SECTION_CUE = re.compile(
    r"^(?:history\b|background\b)",
    re.IGNORECASE,
)
_PRIOR_WORK_CUE = re.compile(
    r"\b(?:following previous approaches|previous approaches|prior work|"
    r"has been shown|have been shown|BIBREF\d+\s+(?:develop|report|show|use)|"
    r"they (?:report|were))\b",
    re.IGNORECASE,
)
_CITATION_CLAIM_CUE = re.compile(r"\bBIBREF\d+\b", re.IGNORECASE)
_CURRENT_PAPER_CUE = re.compile(
    r"\b(?:we|our|this (?:work|study|paper))\b",
    re.IGNORECASE,
)
_CURRENT_RESULT_CUE = re.compile(
    r"(?:\b(?:we|our|this (?:work|study|paper))\b.{0,180}"
    r"\b(?:achieved|found|showed|improved|improves|outperformed|"
    r"outperforms|gained|gains|yielded|yields|reached|reaches)\b|"
    r"\bthe results?\b.{0,80}\b(?:show|shows|showed|confirm|confirms|confirmed|"
    r"indicate|indicates|demonstrate|demonstrates)\b|"
    r"\btable(?:\s+TABREF\d+)?\b.{0,80}\b(?:show|shows|showed|illustrate|"
    r"illustrates|present|presents)\b)",
    re.IGNORECASE | re.DOTALL,
)
_PAPER_ROADMAP_CUE = re.compile(
    r"\b(?:section\s+\d+\s+(?:discusses|presents)|we will present|will be introduced)\b",
    re.IGNORECASE,
)
_FUTURE_ONLY_CUE = re.compile(
    r"\b(?:will conduct experiments|future work|future direction|in the future|"
    r"want to evaluate|want to investigate|would be interesting to experiment|"
    r"worthy of exploration)\b",
    re.IGNORECASE,
)
_HYPOTHESIS_ONLY_CUE = re.compile(
    r"\b(?:we believe|we hypothesi[sz]e|we expect|we predict|"
    r"it is to be expected)\b",
    re.IGNORECASE,
)
_WEAK_PROMISE_CUE = re.compile(
    r"\bshows? great promise\b",
    re.IGNORECASE,
)
_PURPOSE_OUTCOME_CUE = re.compile(
    r"\b(?:so as to|in order to|to)\s+(?:achieve|improve|increase|maximi[sz]e)\b",
    re.IGNORECASE,
)
_MODEL_LABEL_CUE = re.compile(
    r"(?:bi?lstm|cnn|faster-r?cnn|gpt(?:-\d+)?|lr|rnn|transformer)",
    re.IGNORECASE,
)
_RESULT_VALUE_CUE = re.compile(
    r"\b(how much|by how much|what (?:is|was|were) (?:the )?(?:result|score|value)|"
    r"result|results|score|performance|accuracy|f1|bleu|rouge)\b",
    re.IGNORECASE,
)
_DIRECT_RESULT_QUERY_CUE = re.compile(
    r"\b(result|results|performance|score|accuracy|f1|bleu|rouge|"
    r"how much better|improvement|improve|outperform(?:ed|s|ing)?)\b",
    re.IGNORECASE,
)
_METRIC_CUE = re.compile(
    r"\b(F1|F-?score|F-?measure|BLEU|ROUGE(?:-[A-Za-z0-9]+)?|acc(?:uracy)?|precision|"
    r"recall|MRR|nDCG|AUC(?:-ROC)?|ERR|H@\d+)\b",
    re.IGNORECASE,
)
_DECIMAL_VALUE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(%)?")
_PAPER_ROLE_PATTERNS = {
    QA.Dataset: (
        re.compile(
            r"\b([A-Z][A-Za-z0-9_-]{1,40}(?:\s+[A-Z][A-Za-z0-9_-]{1,40}){0,2})\s+"
            r"(?:dataset|corpus|benchmark)\b"
        ),
    ),
    QA.Metric: (
        re.compile(
            r"\b(F1|F-?measure|BLEU|ROUGE(?:-[A-Za-z0-9]+)?|accuracy|precision|"
            r"recall|MRR|nDCG|AUC(?:-ROC)?|ERR|H@\d+)\b",
            re.IGNORECASE,
        ),
    ),
    QA.Model: (
        re.compile(
            r"\b([A-Z][A-Za-z0-9_-]{1,40}(?:\s+[A-Z][A-Za-z0-9_-]{1,40}){0,1})\s+"
            r"(?:model|system|architecture)\b"
        ),
    ),
    QA.Method: (
        re.compile(
            r"\b([A-Z][A-Za-z0-9_-]{1,40}(?:\s+[A-Z][A-Za-z0-9_-]{1,40}){0,1})\s+"
            r"(?:method|approach|technique)\b"
        ),
    ),
}
_PAPER_ENTITY_STOP_LABELS = {
    "baseline",
    "neural",
    "new",
    "our",
    "proposed",
    "the",
    "their",
    "this",
    "if",
}
_PAPER_DATASET_STOP_LABELS = {
    "ape",
    "nlp",
    "parallel corpus",
    "twitter",
}
_QUERY_TYPE_ALIASES = {
    QA.Dataset: {"dataset", "datasets", "corpus", "corpora"},
    QA.Metric: {"metric", "metrics", "measure", "measures"},
    QA.Model: {"model", "models", "architecture", "architectures"},
    QA.Method: {"method", "methods", "approach", "approaches", "technique", "techniques"},
    QA.Task: {"task", "tasks", "problem", "problems"},
}

_QUERY_PHRASE_BOUNDARIES = {
    "a",
    "an",
    "are",
    "as",
    "at",
    "be",
    "by",
    "did",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


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


@dataclass(frozen=True)
class GraphChunkCandidate:
    chunk_id: str
    score: float
    query_concepts: list[str]
    matched_concepts: list[str]
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
        query_linking_threshold: float | None = None,
        linking_limit: int = 5,
        query_type_intent: bool = False,
        query_phrase_linking: bool = False,
        query_phrase_margin: float = 0.03,
        query_phrase_secondary_threshold_delta: float = 0.05,
    ) -> None:
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
        self._semantic_encoder = semantic_encoder
        self.linking_method = linking_method
        self.linking_threshold = linking_threshold
        self.query_linking_threshold = (
            linking_threshold
            if query_linking_threshold is None
            else query_linking_threshold
        )
        self.linking_limit = linking_limit
        self.query_type_intent = query_type_intent
        self.query_phrase_linking = query_phrase_linking
        self.query_phrase_margin = query_phrase_margin
        self.query_phrase_secondary_threshold_delta = query_phrase_secondary_threshold_delta
        self._concept_embeddings: NDArray[np.float32] | None = None
        self._concept_aliases = self._load_concept_aliases()
        self._configured_concept_cache: dict[str, tuple[URIRef, ...]] = {}
        self._configured_query_concept_cache: dict[str, tuple[URIRef, ...]] = {}

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
            if object_type in concept_types
            and isinstance(subject, URIRef)
            and not local_name(subject).startswith("Sample")
            and self._retrieval_enabled(subject)
        }
        aliases: dict[URIRef, set[str]] = {}
        for concept in concepts:
            names = {local_name(concept)}
            for predicate in (RDFS.label, SKOS.prefLabel, SKOS.altLabel):
                names.update(str(value) for value in self.graph.objects(concept, predicate))
            aliases[concept] = {normalize_text(name) for name in names if normalize_text(name)}
        return aliases

    def _retrieval_enabled(self, resource: URIRef) -> bool:
        return (
            resource,
            QA.retrievalEnabled,
            Literal(False, datatype=XSD.boolean),
        ) not in self.graph

    def identify_concepts(self, text: str) -> list[URIRef]:
        normalized = f" {normalize_text(text)} "
        matches = [
            concept
            for concept, aliases in self._concept_aliases.items()
            if any(f" {alias} " in normalized for alias in aliases)
        ]
        return sorted(matches, key=local_name)

    def vocabulary_labels(self) -> set[str]:
        """Return preferred labels for concepts available to the local linker."""
        return {self.preferred_label(concept) for concept in self._concept_aliases}

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

    def semantic_candidates(
        self, text: str, *, limit: int = 5
    ) -> list[ConceptLink]:
        """Return the nearest ontology concepts without applying an acceptance threshold."""
        return self.semantic_candidates_batch([text], limit=limit)[0]

    def semantic_candidates_batch(
        self, texts: list[str], *, limit: int = 5
    ) -> list[list[ConceptLink]]:
        """Return nearest candidates for auditing misses without changing linking policy."""
        if limit < 1:
            raise ValueError("limit must be at least 1")
        return self.link_concepts_batch(
            texts,
            ConceptLinkingMethod.SEMANTIC,
            threshold=0.0,
            limit=limit,
        )

    def query_phrases(self, text: str, *, max_ngram: int = 5) -> list[str]:
        """Extract conservative content phrases without requiring a POS tagger.

        The full normalized query is retained as a fallback. Additional candidates are
        contiguous content spans and multi-word n-grams whose boundary tokens are not
        common question/function words. Single-token semantic phrases are intentionally
        excluded because they create too many ambiguous ontology matches.
        """
        normalized = normalize_text(text)
        if not normalized:
            return []
        tokens = normalized.split()
        phrases = [normalized]

        segments: list[list[str]] = []
        current: list[str] = []
        for token in tokens:
            if token in _QUERY_PHRASE_BOUNDARIES:
                if current:
                    segments.append(current)
                    current = []
            else:
                current.append(token)
        if current:
            segments.append(current)

        for segment in segments:
            upper = min(max_ngram, len(segment))
            for size in range(upper, 1, -1):
                for start in range(len(segment) - size + 1):
                    phrases.append(" ".join(segment[start : start + size]))

        return list(dict.fromkeys(phrases))

    def link_query_concepts(
        self,
        text: str,
        *,
        threshold: float | None = None,
        limit: int | None = None,
        margin: float | None = None,
    ) -> list[ConceptLink]:
        """Link a question using exact aliases plus phrase-level semantic candidates."""
        active_threshold = self.query_linking_threshold if threshold is None else threshold
        active_limit = self.linking_limit if limit is None else limit
        active_margin = self.query_phrase_margin if margin is None else margin

        links: dict[str, ConceptLink] = {
            link.concept: link
            for link in self.link_concepts(
                text,
                ConceptLinkingMethod.ALIAS,
                threshold=active_threshold,
                limit=active_limit,
            )
        }
        if (
            self.linking_method not in {ConceptLinkingMethod.SEMANTIC, ConceptLinkingMethod.HYBRID}
            or self._semantic_encoder is None
        ):
            return sorted(links.values(), key=lambda link: (-link.score, link.concept))[
                :active_limit
            ]

        phrases = self.query_phrases(text)
        candidates_by_phrase = self.semantic_candidates_batch(phrases, limit=2)
        for candidates in candidates_by_phrase:
            if not candidates:
                continue
            best = candidates[0]
            runner_up_score = candidates[1].score if len(candidates) > 1 else 0.0
            semantic_threshold = active_threshold + (
                self.query_phrase_secondary_threshold_delta if links else 0.0
            )
            if (
                best.score < semantic_threshold
                or best.score - runner_up_score < active_margin
            ):
                continue
            existing = links.get(best.concept)
            if existing is None or best.score > existing.score:
                links[best.concept] = best

        return sorted(links.values(), key=lambda link: (-link.score, link.concept))[
            :active_limit
        ]

    def configured_concepts(self, text: str) -> list[URIRef]:
        """Link text using the strategy configured for the retrieval pipeline."""
        return self.configured_concepts_batch([text])[0]

    def identify_query_type_concepts(self, text: str) -> list[URIRef]:
        """Find generic ontology classes explicitly requested by a question."""
        normalized = f" {normalize_text(text)} "
        return sorted(
            (
                concept_type
                for concept_type, aliases in _QUERY_TYPE_ALIASES.items()
                if any(f" {alias} " in normalized for alias in aliases)
            ),
            key=local_name,
        )

    def configured_query_concepts(self, text: str) -> list[URIRef]:
        """Link a query and optionally include its requested ontology entity type."""
        cached = self._configured_query_concept_cache.get(text)
        if cached is None:
            links = (
                self.link_query_concepts(text)
                if self.query_phrase_linking
                else self.link_concepts(
                    text,
                    self.linking_method,
                    threshold=self.query_linking_threshold,
                    limit=self.linking_limit,
                )
            )
            known_by_name = {
                local_name(concept): concept for concept in self._concept_aliases
            }
            cached = tuple(
                known_by_name[link.concept]
                for link in links
                if link.concept in known_by_name
            )
            self._configured_query_concept_cache[text] = cached
        concepts = list(cached)
        if self.query_type_intent:
            concepts.extend(self.identify_query_type_concepts(text))
        return sorted(set(concepts), key=local_name)

    def configured_concepts_batch(self, texts: list[str]) -> list[list[URIRef]]:
        """Link configured concepts for many texts using one embedding batch."""
        missing_texts = list(
            dict.fromkeys(
                text for text in texts if text not in self._configured_concept_cache
            )
        )
        linked = self.link_concepts_batch(
            missing_texts,
            self.linking_method,
            threshold=self.linking_threshold,
            limit=self.linking_limit,
        )
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        for text, links in zip(missing_texts, linked, strict=True):
            self._configured_concept_cache[text] = tuple(
                known_by_name[link.concept]
                for link in links
                if link.concept in known_by_name
            )
        return [list(self._configured_concept_cache[text]) for text in texts]

    def index_chunks(self, chunks: list[Chunk]) -> tuple[list[Chunk], int]:
        """Annotate chunks and add document/page/chunk facts to the in-memory graph."""
        annotated: list[Chunk] = []
        concept_links = 0

        linked_chunks = self.configured_concepts_batch([chunk.text for chunk in chunks])
        for chunk, concepts in zip(chunks, linked_chunks, strict=True):
            document = URIRef(f"{QA}document-{chunk.document_id}")
            section = URIRef(f"{QA}section-{chunk.document_id}-page-{chunk.page}")
            chunk_resource = URIRef(f"{QA}chunk-{chunk.id}")
            self.graph.add((document, RDF.type, QA.Paper))
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

            self._index_result_context(document, chunk_resource, chunk.text, concepts)

            annotated.append(
                chunk.model_copy(update={"concepts": [local_name(value) for value in concepts]})
            )

        return annotated, concept_links

    def _index_result_context(
        self,
        document: URIRef,
        chunk_resource: URIRef,
        text: str,
        concepts: list[URIRef],
    ) -> None:
        """Create paper-scoped Result facts from one evidence chunk.

        This is deliberately conservative: a Result is created only when the chunk
        contains typed experimental entities and either a metric or an explicit
        result cue. It is a transparent baseline, not a claim of full IE quality.
        """
        paper_entities = self._extract_paper_scoped_entities(document, text)
        models = [value for value in concepts if self._is_instance_of(value, QA.Model)]
        models.extend(paper_entities[QA.Model])
        methods = [
            value
            for value in concepts
            if value not in models and self._is_instance_of(value, QA.Method)
        ]
        methods.extend(paper_entities[QA.Method])
        datasets = [
            value
            for value in concepts
            if self._is_instance_of(value, QA.Dataset)
            and normalize_text(
                str(self.graph.value(value, SKOS.prefLabel) or local_name(value))
            )
            not in _PAPER_DATASET_STOP_LABELS
        ]
        datasets.extend(paper_entities[QA.Dataset])
        metrics = [value for value in concepts if self._is_instance_of(value, QA.Metric)]
        metrics.extend(paper_entities[QA.Metric])
        typed_dimensions = sum(bool(values) for values in (models, methods, datasets, metrics))
        metric_values = self._extract_metric_values(text)
        outcome_text = _PURPOSE_OUTCOME_CUE.sub("", text)
        has_outcome = _RESULT_OUTCOME_CUE.search(outcome_text) is not None
        has_current_result = _CURRENT_RESULT_CUE.search(outcome_text) is not None
        if (
            _NON_RESULT_SECTION_CUE.search(text)
            or _PRIOR_WORK_SECTION_CUE.search(text)
            or _PAPER_ROADMAP_CUE.search(text)
            or (
                (
                    _PRIOR_WORK_CUE.search(text)
                    or (
                        _CITATION_CLAIM_CUE.search(text)
                        and not _CURRENT_PAPER_CUE.search(text)
                    )
                )
                and not has_current_result
                and not _RESULT_SECTION_CUE.search(text)
            )
            or (
                not metric_values
                and (
                    (
                        (
                            _FUTURE_ONLY_CUE.search(text)
                            or _WEAK_PROMISE_CUE.search(text)
                        )
                        and not has_current_result
                    )
                    or (
                        _HYPOTHESIS_ONLY_CUE.search(text)
                        and not _RESULT_SECTION_CUE.search(text)
                    )
                )
            )
        ):
            return
        if not (
            (metric_values and typed_dimensions >= 1)
            or (
                (has_outcome or _RESULT_SECTION_CUE.search(text))
                and typed_dimensions >= 2
            )
            or (has_current_result and typed_dimensions >= 1)
        ):
            return

        chunk_name = local_name(chunk_resource)
        result = URIRef(f"{QA}result-{chunk_name}")
        self.graph.add((result, RDF.type, QA.Result))
        self.graph.add((document, QA.hasResult, result))
        self.graph.add((result, QA.resultOf, document))
        self.graph.add((result, QA.hasEvidence, chunk_resource))
        self.graph.add((chunk_resource, QA.isEvidenceFor, result))
        self.graph.add((result, QA.resultNote, Literal(text[:1000])))

        for value in methods:
            self.graph.add((result, QA.resultUsesMethod, value))
            self.graph.add((document, QA.usesMethod, value))
        for value in models:
            self.graph.add((result, QA.resultUsesModel, value))
            self.graph.add((document, QA.usesMethod, value))
        for value in datasets:
            self.graph.add((result, QA.resultUsesDataset, value))
            self.graph.add((document, QA.usesDataset, value))
        for value in metrics:
            self.graph.add((result, QA.measuredBy, value))
            self.graph.add((document, QA.evaluatedBy, value))
        for value in {value for values in paper_entities.values() for value in values}:
            self.graph.add((chunk_resource, QA.mentionsConcept, value))
        if metrics:
            for value in metric_values:
                self.graph.add(
                    (result, QA.metricValue, Literal(value, datatype=XSD.decimal))
                )

    @staticmethod
    def _extract_metric_values(text: str) -> list[str]:
        values: list[str] = []
        sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
        for sentence in sentences:
            if not _METRIC_CUE.search(sentence):
                continue
            for match in _DECIMAL_VALUE.finditer(sentence):
                raw, percent = match.groups()
                # Integers without a percent sign are commonly years, counts or table IDs.
                if not percent and "." not in raw:
                    continue
                number = float(raw)
                if percent:
                    number /= 100.0
                if number < 0 or number > 100:
                    continue
                normalized = f"{number:.8f}".rstrip("0").rstrip(".")
                if normalized not in values:
                    values.append(normalized)
        return values

    def _extract_paper_scoped_entities(
        self, document: URIRef, text: str
    ) -> dict[URIRef, list[URIRef]]:
        entities: dict[URIRef, list[URIRef]] = {
            concept_type: [] for concept_type in _PAPER_ROLE_PATTERNS
        }
        document_name = local_name(document)
        for concept_type, patterns in _PAPER_ROLE_PATTERNS.items():
            labels: set[str] = set()
            for pattern in patterns:
                for match in pattern.finditer(text):
                    label = match.group(1).strip(" -_,.;:()")
                    label = re.sub(
                        r"^(?:the|a|an|this|our|their|proposed|new)\s+",
                        "",
                        label,
                        flags=re.IGNORECASE,
                    )
                    normalized_label = normalize_text(label)
                    invalid_dataset = (
                        concept_type == QA.Dataset
                        and normalized_label in _PAPER_DATASET_STOP_LABELS
                    )
                    unresolved_marker = re.search(
                        r"\b(?:bibref|inlineform)\d+\b", normalized_label
                    )
                    if (
                        label
                        and normalized_label not in _PAPER_ENTITY_STOP_LABELS
                        and not invalid_dataset
                        and unresolved_marker is None
                    ):
                        labels.add(label)
            for label in sorted(labels, key=str.lower):
                target_type = concept_type
                if concept_type == QA.Method and _MODEL_LABEL_CUE.fullmatch(label):
                    target_type = QA.Model
                slug = normalize_text(label).replace(" ", "-")
                if not slug:
                    continue
                resource = URIRef(
                    f"{QA}paper-entity-{document_name}-{local_name(target_type)}-{slug}"
                )
                self.graph.add((resource, RDF.type, target_type))
                self.graph.add((resource, SKOS.prefLabel, Literal(label)))
                entities[target_type].append(resource)
        return entities

    def is_chunk_indexed(self, chunk_id: str) -> bool:
        """Return whether a chunk passed through ontology indexing, even with no links."""
        chunk_resource = URIRef(f"{QA}chunk-{chunk_id}")
        return (chunk_resource, RDF.type, QA.Chunk) in self.graph

    def graph_chunk_candidates(
        self,
        query: str,
        *,
        document_id: str | None = None,
        include_related: bool = True,
        limit: int = 20,
    ) -> list[GraphChunkCandidate]:
        """Retrieve chunks through query-concept graph links.

        Exact concept matches receive weight 1.0 and one-hop ontology neighbors 0.5.
        The optional document scope is enforced through Paper -> Section -> Chunk edges.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")
        query_concepts = self.configured_query_concepts(query)
        if not query_concepts:
            return []

        allowed_chunks: set[URIRef] | None = None
        if document_id is not None:
            document = URIRef(f"{QA}document-{document_id}")
            sections = self.graph.objects(document, QA.hasSection)
            allowed_chunks = {
                chunk
                for section in sections
                for chunk in self.graph.objects(section, QA.hasChunk)
                if isinstance(chunk, URIRef)
            }

        concept_weights: dict[URIRef, float] = {
            concept: 1.0 for concept in query_concepts
        }
        if include_related:
            for concept in query_concepts:
                for neighbor in self._neighbors(concept):
                    concept_weights.setdefault(neighbor, 0.5)

        scores: dict[URIRef, float] = {}
        matches: dict[URIRef, set[URIRef]] = {}
        for concept, weight in concept_weights.items():
            for chunk in self.graph.subjects(QA.mentionsConcept, concept):
                if not isinstance(chunk, URIRef):
                    continue
                if allowed_chunks is not None and chunk not in allowed_chunks:
                    continue
                scores[chunk] = min(scores.get(chunk, 0.0) + weight, 1.0)
                matches.setdefault(chunk, set()).add(concept)

        ranked = sorted(
            scores,
            key=lambda chunk: (-scores[chunk], local_name(chunk)),
        )[:limit]
        query_names = [local_name(concept) for concept in query_concepts]
        candidates: list[GraphChunkCandidate] = []
        for chunk in ranked:
            matched_names = sorted(local_name(value) for value in matches[chunk])
            chunk_name = local_name(chunk)
            chunk_id = chunk_name.removeprefix("chunk-")
            candidates.append(
                GraphChunkCandidate(
                    chunk_id=chunk_id,
                    score=scores[chunk],
                    query_concepts=query_names,
                    matched_concepts=matched_names,
                    explanation=(
                        "Graph candidate via mentionsConcept: "
                        + ", ".join(matched_names)
                        + "."
                    ),
                )
            )
        return candidates

    def _neighbors(self, concept: URIRef) -> set[URIRef]:
        predicates = {SKOS.broader, SKOS.narrower, SKOS.related, QA.relatedTo}
        neighbors: set[URIRef] = set()
        for predicate in predicates:
            neighbors.update(
                value
                for value in self.graph.objects(concept, predicate)
                if isinstance(value, URIRef) and self._retrieval_enabled(value)
            )
            neighbors.update(
                value
                for value in self.graph.subjects(predicate, concept)
                if isinstance(value, URIRef) and self._retrieval_enabled(value)
            )
        return neighbors

    def preferred_label(self, concept: URIRef) -> str:
        label = next(iter(self.graph.objects(concept, SKOS.prefLabel)), None)
        return str(label) if isinstance(label, Literal) else local_name(concept)

    def expand_query(self, query: str) -> QueryExpansion:
        concepts = self.configured_query_concepts(query)
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
        query_concepts = self.configured_query_concepts(query)
        chunk_concepts = self.configured_concepts(text)
        return self._score_concepts(query_concepts, chunk_concepts)

    def score_context(
        self,
        query: str,
        text: str,
        *,
        query_concepts: list[str] | None = None,
        chunk_concepts: list[str] | None = None,
        chunk_id: str | None = None,
    ) -> OntologyMatch:
        """Score ontology evidence while respecting the question and passage context.

        The original graph-only score treats every linked concept as equally reliable.
        This variant downweights broad/hub concepts and semantic-only links, recognises
        the entity type explicitly requested by the question, and leaves final fusion
        with the retrieval score to the retriever.
        """
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        resolved_query = (
            [known_by_name[name] for name in query_concepts or [] if name in known_by_name]
            if query_concepts is not None
            else self.configured_concepts(query)
        )
        resolved_chunks = (
            [known_by_name[name] for name in chunk_concepts or [] if name in known_by_name]
            if chunk_concepts is not None
            else self.configured_concepts(text)
        )
        requested_types = self.identify_query_type_concepts(query)

        topical = self._score_concepts(resolved_query, resolved_chunks)
        type_matches = [
            concept
            for concept in resolved_chunks
            if any(self._is_instance_of(concept, requested) for requested in requested_types)
        ]
        type_score = 1.0 if type_matches else 0.0

        if resolved_query:
            raw_score = topical.score
            if requested_types:
                raw_score = (0.8 * raw_score) + (0.2 * type_score)
        elif requested_types:
            # A generic request such as "which dataset" has no topical anchor.
            # Rewarding every passage that contains the requested entity type
            # causes unrelated datasets/models to move ahead of stronger retrieval
            # evidence. Keep the type visible for explanation, but do not award a
            # ranking bonus until the query also links to a topical concept.
            raw_score = 0.0
        else:
            raw_score = 0.0

        result_score, result_reason = self._score_result_context(
            query,
            requested_types,
            resolved_query,
            chunk_id,
        )
        raw_score = max(raw_score, result_score)

        query_support = self._explicit_support_ratio(query, resolved_query)
        chunk_support = self._explicit_support_ratio(text, resolved_chunks)
        lexical_reliability = 0.7 + (0.15 * query_support) + (0.15 * chunk_support)
        specificity = self._query_specificity(resolved_query)
        if resolved_query and set(resolved_query).issubset(resolved_chunks):
            # Exact concepts explicitly supported on both sides are strong evidence,
            # even when the concept is a broad graph hub such as NLP.
            specificity = 1.0
        score = min(max(raw_score * lexical_reliability * specificity, 0.0), 1.0)

        reasons = [topical.explanation] if topical.score > 0 else []
        if requested_types:
            requested = ", ".join(local_name(value) for value in requested_types)
            if type_matches:
                matched = ", ".join(local_name(value) for value in type_matches)
                reasons.append(f"Question requests {requested}; passage contains {matched}.")
            else:
                reasons.append(f"Question requests {requested}; no matching passage type.")
        if result_reason:
            reasons.append(result_reason)
        reasons.append(
            "Context reliability: "
            f"query={query_support:.2f}, passage={chunk_support:.2f}, "
            f"specificity={specificity:.2f}."
        )

        displayed_query = [local_name(value) for value in resolved_query]
        displayed_query.extend(local_name(value) for value in requested_types)
        return OntologyMatch(
            score=score,
            query_concepts=list(dict.fromkeys(displayed_query)),
            chunk_concepts=[local_name(value) for value in resolved_chunks],
            explanation=" ".join(reasons),
        )

    def _score_result_context(
        self,
        query: str,
        requested_types: list[URIRef],
        query_concepts: list[URIRef],
        chunk_id: str | None,
    ) -> tuple[float, str]:
        if not chunk_id:
            return 0.0, ""
        if not query_concepts and not _DIRECT_RESULT_QUERY_CUE.search(query):
            return 0.0, ""
        chunk_resource = URIRef(f"{QA}chunk-{chunk_id}")
        results = [
            value
            for value in self.graph.objects(chunk_resource, QA.isEvidenceFor)
            if isinstance(value, URIRef)
        ]
        if not results:
            return 0.0, ""

        type_predicates = {
            QA.Method: (QA.resultUsesMethod, QA.resultUsesModel),
            QA.Model: (QA.resultUsesModel,),
            QA.Dataset: (QA.resultUsesDataset,),
            QA.Metric: (QA.measuredBy,),
        }
        requested_dimensions = [
            value for value in requested_types if value in type_predicates
        ]
        asks_for_value = bool(_RESULT_VALUE_CUE.search(query))
        best_score = 0.0
        best_facts: list[str] = []
        for result in results:
            entities = {
                value
                for predicate in (
                    QA.resultUsesMethod,
                    QA.resultUsesModel,
                    QA.resultUsesDataset,
                    QA.measuredBy,
                )
                for value in self.graph.objects(result, predicate)
                if isinstance(value, URIRef)
            }
            dimension_matches = sum(
                any(next(self.graph.objects(result, predicate), None) is not None for predicate in type_predicates[requested])
                for requested in requested_dimensions
            )
            value_match = asks_for_value and any(
                True for _ in self.graph.objects(result, QA.metricValue)
            )
            requirements = len(requested_dimensions) + int(asks_for_value)
            matched = dimension_matches + int(value_match)
            if requirements == 0:
                continue

            anchor_match = any(
                concept in entities
                or any(entity in self._neighbors(concept) for entity in entities)
                for concept in query_concepts
            )
            coverage = matched / requirements
            score = (0.55 * coverage) + (0.20 if anchor_match else 0.0)
            if score > best_score:
                best_score = score
                best_facts = [local_name(value) for value in sorted(entities, key=local_name)]

        if best_score == 0:
            return 0.0, ""
        return min(best_score, 0.85), (
            "Paper-scoped Result context matched: " + ", ".join(best_facts) + "."
        )

    def _explicit_support_ratio(self, text: str, concepts: list[URIRef]) -> float:
        if not concepts:
            return 0.0
        normalized = f" {normalize_text(text)} "
        supported = sum(
            any(f" {alias} " in normalized for alias in self._concept_aliases.get(concept, set()))
            for concept in concepts
        )
        return supported / len(concepts)

    def _query_specificity(self, concepts: list[URIRef]) -> float:
        """Downweight broad graph hubs without discarding exact topic evidence."""
        if not concepts:
            return 1.0
        values = []
        for concept in concepts:
            degree = len(self._neighbors(concept))
            values.append(max(0.65, 1.0 - (0.04 * min(degree, 8))))
        return sum(values) / len(values)

    def score_concept_names(
        self, query_concepts: list[str], chunk_concepts: list[str]
    ) -> OntologyMatch:
        known_by_name = {local_name(concept): concept for concept in self._concept_aliases}
        known_by_name.update(
            {local_name(concept_type): concept_type for concept_type in _QUERY_TYPE_ALIASES}
        )
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
                if self._is_instance_of(chunk_concept, query_concept):
                    best_score = max(best_score, 0.5)
                    reasons.append(
                        f"Requested type: {local_name(chunk_concept)} is a "
                        f"{local_name(query_concept)}"
                    )
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

    def _is_instance_of(self, resource: URIRef, requested_type: URIRef) -> bool:
        pending = [
            value
            for value in self.graph.objects(resource, RDF.type)
            if isinstance(value, URIRef)
        ]
        visited: set[URIRef] = set()
        while pending:
            current = pending.pop()
            if current == requested_type:
                return True
            if current in visited:
                continue
            visited.add(current)
            pending.extend(
                value
                for value in self.graph.objects(current, RDFS.subClassOf)
                if isinstance(value, URIRef)
            )
        return False

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
