import re
from dataclasses import dataclass
from typing import Protocol

from app.agent.ollama import LocalAnswer
from app.models import (
    AgentStatus,
    AgentStep,
    AskResponse,
    Citation,
    SearchMethod,
    SearchResult,
)
from app.rag.retriever import InMemoryHybridRetriever, tokenize

INSUFFICIENT_EVIDENCE_MESSAGE = "Tài liệu hiện chưa cung cấp đủ thông tin để trả lời câu hỏi này."
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")
_PAGE_HEADER = re.compile(
    r"^Tài liệu kiểm thử AI Agent \+ RAG \+ Ontology Trang \d+\s+\d+\.\s*",
    re.IGNORECASE,
)
_EVIDENCE_STOPWORDS = {
    "ai",
    "bao",
    "co",
    "cua",
    "duoc",
    "gi",
    "hay",
    "khong",
    "la",
    "lieu",
    "mai",
    "mot",
    "nao",
    "ngay",
    "noi",
    "nhung",
    "tai",
    "the",
    "thi",
    "trong",
    "va",
    "ve",
}


class AnswerGenerator(Protocol):
    def generate(self, question: str, evidence: list[SearchResult]) -> str | LocalAnswer: ...


@dataclass(frozen=True)
class EvidenceDecision:
    accepted: bool
    confidence: float
    reason: str


@dataclass(frozen=True)
class EvidenceGateConfig:
    # Selected on the first half of QASPER development papers and verified on
    # the second half. Held-out data is intentionally not used here.
    ontology_threshold: float = 0.80
    ontology_min_overlap: int = 0
    semantic_threshold: float = 0.55
    semantic_min_overlap: int = 2
    combined_semantic_threshold: float = 0.40
    combined_min_overlap: int = 3
    cross_encoder_threshold: float = 0.50
    cross_encoder_min_overlap: int = 3


class EvidenceGate:
    """Rejects weak retrieval results before any answer generator is called."""

    def __init__(self, config: EvidenceGateConfig | None = None) -> None:
        self.config = config or EvidenceGateConfig()

    def evaluate(
        self,
        question: str,
        results: list[SearchResult],
    ) -> EvidenceDecision:
        if not results:
            return EvidenceDecision(False, 0.0, "Không tìm thấy đoạn bằng chứng nào.")

        top = results[0]
        ontology_score = top.ontology_score or 0.0
        semantic_score = top.semantic_score or 0.0
        bm25_score = top.bm25_score or 0.0
        question_terms = {term for term in tokenize(question) if term not in _EVIDENCE_STOPWORDS}
        evidence_terms = set(tokenize(" ".join(item.text for item in results[:3])))
        lexical_overlap = len(question_terms.intersection(evidence_terms))

        if (
            top.method == SearchMethod.HYBRID_ONTOLOGY_CROSS_ENCODER
            and top.score >= self.config.cross_encoder_threshold
            and lexical_overlap >= self.config.cross_encoder_min_overlap
        ):
            return EvidenceDecision(
                True,
                min(1.0, top.score),
                "Bằng chứng đạt ngưỡng cross-encoder đã hiệu chỉnh.",
            )

        if (
            top.query_concepts
            and ontology_score >= self.config.ontology_threshold
            and lexical_overlap >= self.config.ontology_min_overlap
        ):
            confidence = min(1.0, 0.55 + (0.45 * ontology_score))
            return EvidenceDecision(
                True,
                confidence,
                "Bằng chứng có concept khớp hoặc liên quan trong Ontology.",
            )

        if (
            semantic_score >= self.config.semantic_threshold
            and lexical_overlap >= self.config.semantic_min_overlap
        ):
            return EvidenceDecision(
                True,
                min(1.0, semantic_score),
                "Bằng chứng có độ tương đồng ngữ nghĩa cao.",
            )

        if (
            bm25_score > 0
            and semantic_score >= self.config.combined_semantic_threshold
            and lexical_overlap >= self.config.combined_min_overlap
        ):
            confidence = min(1.0, 0.5 + (semantic_score * 0.4))
            return EvidenceDecision(
                True,
                confidence,
                "Bằng chứng đồng thời khớp từ khóa và ngữ nghĩa.",
            )

        confidence = min(0.49, max(ontology_score, semantic_score))
        return EvidenceDecision(
            False,
            confidence,
            "Tín hiệu từ khóa, ngữ nghĩa và Ontology chưa đủ mạnh.",
        )


class ExtractiveAnswerGenerator:
    """Safe development generator; replace with an LLM provider in the next iteration."""

    def generate(self, question: str, evidence: list[SearchResult]) -> str:
        if not evidence:
            return INSUFFICIENT_EVIDENCE_MESSAGE

        query_tokens = set(tokenize(question))
        if evidence[0].expanded_query:
            query_tokens.update(tokenize(evidence[0].expanded_query))

        candidates: list[tuple[int, int, int, str]] = []
        for result_rank, result in enumerate(evidence[:3]):
            cleaned = _PAGE_HEADER.sub("", result.text).strip()
            for sentence_rank, sentence in enumerate(_SENTENCE_BOUNDARY.split(cleaned)):
                sentence = sentence.strip()
                if len(sentence) < 20:
                    continue
                overlap = len(query_tokens.intersection(tokenize(sentence)))
                priority = (overlap * 10) - (result_rank * 3) - sentence_rank
                candidates.append((priority, overlap, sentence_rank, sentence))

        if not candidates:
            return evidence[0].text.strip()

        best = max(candidates, key=lambda item: item[0])
        return best[3]


class DocumentQuestionAgent:
    def __init__(
        self,
        retriever: InMemoryHybridRetriever,
        *,
        evidence_gate: EvidenceGate | None = None,
        answer_generator: AnswerGenerator | None = None,
        retrieval_method: SearchMethod = SearchMethod.HYBRID_ONTOLOGY_RERANK,
        generation_evidence_limit: int = 3,
    ) -> None:
        if not 1 <= generation_evidence_limit <= 5:
            raise ValueError("generation_evidence_limit must be between 1 and 5")
        self.retriever = retriever
        self.evidence_gate = evidence_gate or EvidenceGate()
        self.answer_generator = answer_generator or ExtractiveAnswerGenerator()
        self.retrieval_method = retrieval_method
        self.generation_evidence_limit = generation_evidence_limit

    def ask(
        self,
        question: str,
        limit: int = 5,
        document_id: str | None = None,
    ) -> AskResponse:
        trace = [
            AgentStep(
                name="receive_question",
                status="completed",
                detail="Đã tiếp nhận và kiểm tra câu hỏi.",
            )
        ]
        results = self.retriever.search(
            question,
            limit,
            self.retrieval_method,
            document_id,
        )
        trace.append(
            AgentStep(
                name="ontology_retrieval",
                status="completed",
                detail=(
                    f"Đã truy hồi {len(results)} đoạn bằng {self.retrieval_method.value}."
                ),
            )
        )

        decision = self.evidence_gate.evaluate(question, results)
        trace.append(
            AgentStep(
                name="evidence_gate",
                status="accepted" if decision.accepted else "rejected",
                detail=decision.reason,
            )
        )

        first = results[0] if results else None
        if not decision.accepted:
            trace.append(
                AgentStep(
                    name="answer_generation",
                    status="skipped",
                    detail="Không gọi bộ sinh câu trả lời vì evidence chưa đủ mạnh.",
                )
            )
            return AskResponse(
                question=question,
                status=AgentStatus.INSUFFICIENT_EVIDENCE,
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                confidence=decision.confidence,
                query_concepts=first.query_concepts if first else [],
                expanded_query=first.expanded_query if first else None,
                trace=trace,
            )

        generation_evidence = results[: self.generation_evidence_limit]
        generated = self.answer_generator.generate(question, generation_evidence)
        # Source integrity is checked here; semantic entailment still needs evaluation.
        is_llm = isinstance(generated, LocalAnswer)
        if is_llm:
            answer, citations = generated.validated_answer(generation_evidence)
        else:
            answer, citations = generated.strip(), []
        supporting = next(
            (result for result in generation_evidence if answer and answer in result.text),
            None,
        )
        if not answer or (not is_llm and supporting is None):
            trace.extend(
                [
                    AgentStep(
                        name="answer_generation",
                        status="completed",
                        detail=(
                            "LLM không đưa ra câu trả lời có bằng chứng."
                            if is_llm
                            else "Đã nhận câu trả lời từ bộ sinh trích xuất."
                        ),
                    ),
                    AgentStep(
                        name="citation_validation",
                        status="rejected",
                        detail=(
                            "Không có claim để trích dẫn."
                            if is_llm
                            else "Câu trả lời không có đoạn trích khớp trong evidence."
                        ),
                    ),
                ]
            )
            return AskResponse(
                question=question,
                status=AgentStatus.INSUFFICIENT_EVIDENCE,
                answer=INSUFFICIENT_EVIDENCE_MESSAGE,
                confidence=0.0,
                query_concepts=first.query_concepts if first else [],
                expanded_query=first.expanded_query if first else None,
                trace=trace,
            )
        if not is_llm:
            citations = [self._citation(supporting, answer)]
        trace.extend(
            [
                AgentStep(
                    name="answer_generation",
                    status="completed",
                    detail=(
                        "Đã sinh câu trả lời bằng LLM local."
                        if is_llm
                        else "Đã tạo câu trả lời trích xuất từ evidence được chấp nhận."
                    ),
                ),
                AgentStep(
                    name="citation_validation",
                    status="completed",
                    detail=(
                        "Đã kiểm tra ID và quote; chưa xác minh ngữ nghĩa từng claim."
                        if is_llm
                        else "Đã đối chiếu nguyên văn câu trả lời với chunk được trích dẫn."
                    ),
                ),
            ]
        )
        return AskResponse(
            question=question,
            status=AgentStatus.ANSWERED,
            answer=answer,
            confidence=decision.confidence,
            citations=citations,
            query_concepts=first.query_concepts if first else [],
            expanded_query=first.expanded_query if first else None,
            trace=trace,
        )

    @staticmethod
    def _citation(result: SearchResult, quote: str) -> Citation:
        return Citation(
            filename=result.filename,
            page=result.page,
            chunk_id=result.chunk_id,
            quote=quote,
        )
