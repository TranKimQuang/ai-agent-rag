import numpy as np

from app.agent.service import INSUFFICIENT_EVIDENCE_MESSAGE, DocumentQuestionAgent
from app.models import AgentStatus, Chunk
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
