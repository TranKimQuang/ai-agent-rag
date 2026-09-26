import numpy as np
import pytest

from app.agent.service import INSUFFICIENT_EVIDENCE_MESSAGE, DocumentQuestionAgent
from app.models import AgentStatus, Chunk, SearchMethod, SearchResult
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever


class AgentTestEncoder:
    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "question answering" in lowered or "qa " in lowered:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


def make_agent() -> DocumentQuestionAgent:
    retriever = InMemoryHybridRetriever(
        semantic_encoder=AgentTestEncoder(),
        ontology_service=OntologyService(),
    )
    return DocumentQuestionAgent(retriever)


def test_agent_answers_with_valid_citation_when_evidence_is_strong() -> None:
    agent = make_agent()
    agent.retriever.add(
        [
            Chunk(
                id="paper:p1:c1",
                document_id="paper",
                filename="paper.pdf",
                page=1,
                text=(
                    "Question Answering is a branch of Natural Language Processing. "
                    "It answers questions using supporting evidence."
                ),
                concepts=["QuestionAnswering", "NaturalLanguageProcessing"],
            )
        ]
    )

    response = agent.ask("QA thuộc lĩnh vực NLP như thế nào?")

    assert response.status == AgentStatus.ANSWERED
    assert response.citations[0].filename == "paper.pdf"
    assert response.citations[0].page == 1
    assert response.citations[0].chunk_id == "paper:p1:c1"
    assert "Natural Language Processing" in response.answer
    assert response.confidence >= 0.8
    assert response.trace[-1].name == "citation_validation"


def test_agent_refuses_when_no_evidence_exists() -> None:
    response = make_agent().ask("Tài liệu nói gì về vật lý lượng tử?")

    assert response.status == AgentStatus.INSUFFICIENT_EVIDENCE
    assert response.answer == INSUFFICIENT_EVIDENCE_MESSAGE
    assert response.citations == []
    assert any(step.status == "rejected" for step in response.trace)


class FixedRetriever:
    def search(self, *args):
        return [
            SearchResult(
                chunk_id=f"paper:p{page}:c1", document_id="paper",
                filename="paper.pdf", page=page, text=text,
                method=SearchMethod.HYBRID_ONTOLOGY, score=1.0,
                ontology_score=1.0, query_concepts=["QuestionAnswering"],
            )
            for page, text in enumerate([
                "This paragraph discusses a different research method.",
                "Question answering uses evidence to answer questions.",
            ], start=1)
        ]


class FixedGenerator:
    def __init__(self, answer):
        self.answer = answer

    def generate(self, question, evidence):
        return self.answer


def test_citation_points_only_to_actual_answer_source():
    answer = "Question answering uses evidence to answer questions."
    agent = DocumentQuestionAgent(
        FixedRetriever(), answer_generator=FixedGenerator(answer),
    )
    response = agent.ask("What is question answering?")
    assert response.status == AgentStatus.ANSWERED
    assert len(response.citations) == 1
    assert response.citations[0].page == 2
    assert response.citations[0].quote == answer


@pytest.mark.parametrize("answer", ["", "   ", "An unsupported invented answer."])
def test_agent_rejects_empty_or_ungrounded_generated_answer(answer):
    agent = DocumentQuestionAgent(
        FixedRetriever(), answer_generator=FixedGenerator(answer),
    )
    response = agent.ask("What is question answering?")
    assert response.status == AgentStatus.INSUFFICIENT_EVIDENCE
    assert response.citations == []
    assert response.trace[-1].status == "rejected"


def test_empty_retrieval_never_calls_generator():
    class MustNotRun:
        def generate(self, question, evidence):
            raise AssertionError("Generator must not run without evidence")

    agent = make_agent()
    agent.answer_generator = MustNotRun()
    assert agent.ask("Missing evidence?").status == AgentStatus.INSUFFICIENT_EVIDENCE
