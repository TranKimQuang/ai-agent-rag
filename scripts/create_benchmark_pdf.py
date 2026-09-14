# ruff: noqa: ISC004

import json
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

PROJECT_ROOT = Path(__file__).parents[1]
PDF_PATH = PROJECT_ROOT / "output" / "pdf" / "tai-lieu-kiem-thu-ontology-rag.pdf"
DATASET_PATH = PROJECT_ROOT / "evaluation" / "pdf_benchmark.json"
FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD_PATH = Path("C:/Windows/Fonts/arialbd.ttf")

SECTIONS = [
    (
        "1. BM25 và tìm kiếm từ khóa",
        [
            "BM25 là một thuật toán xếp hạng tài liệu dựa trên từ khóa. Thuật toán xem xét "
            "tần suất xuất hiện của từ trong đoạn văn, độ hiếm của từ trong toàn bộ tập tài "
            "liệu và độ dài của đoạn. Những từ hiếm nhưng xuất hiện đúng trong truy vấn thường "
            "đóng góp nhiều hơn vào điểm xếp hạng.",
            "Ưu điểm của BM25 là nhanh, nhẹ và dễ giải thích. Hạn chế chính là phương pháp này "
            "không hiểu tốt từ đồng nghĩa hoặc những cách diễn đạt khác nhau. Ví dụ, truy vấn "
            "'xe hơi' có thể không khớp với đoạn chỉ dùng từ 'ô tô'.",
        ],
    ),
    (
        "2. Semantic Search và embedding",
        [
            "Semantic Search tìm kiếm theo ý nghĩa thay vì chỉ so sánh từ khóa. Câu hỏi và "
            "các chunk được chuyển thành vector embedding bằng một mô hình Sentence "
            "Transformers. Các vector gần nhau thể hiện nội dung có ý nghĩa tương tự.",
            "Cosine similarity được dùng để đo độ gần giữa vector câu hỏi và vector chunk. "
            "Nhờ đó, hệ thống có thể tìm được một đoạn nói về ô tô khi người dùng hỏi về xe "
            "hơi. Hạn chế là semantic search đôi khi chọn đoạn có ý nghĩa chung gần giống nhưng "
            "thiếu thuật ngữ chính xác cần thiết.",
        ],
    ),
    (
        "3. Hybrid Search và Reciprocal Rank Fusion",
        [
            "Hybrid Search kết hợp BM25 với Semantic Search để tận dụng cả từ khóa chính xác và "
            "sự tương đồng về ý nghĩa. Mỗi bộ tìm kiếm tạo ra một bảng xếp hạng chunk độc lập.",
            "Reciprocal Rank Fusion, viết tắt là RRF, kết hợp các bảng xếp hạng dựa trên vị trí "
            "của từng chunk. Một chunk đứng cao ở cả BM25 và Semantic Search sẽ nhận điểm RRF "
            "tốt. RRF không yêu cầu điểm BM25 và cosine similarity phải có cùng thang đo.",
        ],
    ),
    (
        "4. Retrieval-Augmented Generation",
        [
            "Retrieval-Augmented Generation, viết tắt là RAG, tìm các đoạn bằng chứng trước khi "
            "mô hình ngôn ngữ tạo câu trả lời. Các chunk liên quan cùng metadata nguồn được đưa "
            "vào prompt để giới hạn ngữ cảnh của mô hình.",
            "Một hệ thống RAG có kiểm soát phải trả lời dựa trên evidence được cung cấp và kèm "
            "citation gồm tên tài liệu, số trang và chunk ID. Nếu evidence không đủ để kết luận, "
            "hệ thống phải thông báo chưa đủ thông tin thay vì tự suy đoán.",
        ],
    ),
    (
        "5. QASPER và đánh giá evidence",
        [
            "QASPER là một bộ dữ liệu hỏi đáp trên các bài báo khoa học. Mỗi câu hỏi được liên "
            "kết với câu trả lời và các đoạn bằng chứng trong bài báo, vì vậy dữ liệu này phù "
            "hợp để đánh giá retrieval và question answering.",
            "Evidence F1 đo mức độ trùng khớp giữa bằng chứng hệ thống chọn và bằng chứng chuẩn. "
            "Citation Precision đo tỷ lệ citation thực sự chứa thông tin hỗ trợ cho câu trả lời. "
            "Hai chỉ số giúp phân biệt câu trả lời có căn cứ với câu trả lời chỉ nghe hợp lý.",
        ],
    ),
    (
        "6. Ontology và Knowledge Graph",
        [
            "Ontology định nghĩa các lớp khái niệm và quan hệ trong miền tri thức. Trong hệ "
            "thống hỏi đáp tài liệu, các lớp chính có thể gồm Paper, Section, Chunk, Task, "
            "Method, Dataset và Metric. Knowledge Graph chứa các instance và liên kết thực tế "
            "được tạo theo cấu trúc Ontology.",
            "Ontology hỗ trợ query expansion bằng synonym, superclass, subclass và related "
            "concept. Sau Hybrid Search, Ontology-aware re-ranking tăng điểm cho chunk chứa "
            "concept có quan hệ gần với concept của câu hỏi. OntoScore ghi nhận mức phù hợp ngữ "
            "nghĩa có cấu trúc này.",
        ],
    ),
    (
        "7. AI Agent và kiểm tra bằng chứng",
        [
            "AI Agent điều phối các công cụ của hệ thống. Agent nhận câu hỏi, xác định truy vấn, "
            "gọi retrieval, yêu cầu Ontology mở rộng hoặc xếp hạng lại, rồi chuyển evidence phù "
            "hợp cho mô hình ngôn ngữ.",
            "Trước khi trả lời, Agent phải kiểm tra evidence có hỗ trợ kết luận hay không. Câu "
            "trả lời cuối cùng phải kèm filename, page và chunk ID. Nếu không tìm được evidence "
            "đủ tốt, Agent từ chối trả lời để hạn chế hallucination.",
        ],
    ),
    (
        "8. Các chỉ số đánh giá retrieval",
        [
            "Precision at k đo tỷ lệ kết quả đúng trong k chunk đầu tiên. Recall at k đo tỷ lệ "
            "bằng chứng đúng đã được tìm thấy trong k kết quả đầu tiên. Mean Reciprocal Rank, "
            "viết tắt là MRR, đánh giá vị trí của kết quả đúng đầu tiên.",
            "Normalized Discounted Cumulative Gain, hay nDCG, đánh giá chất lượng của toàn bộ "
            "thứ tự xếp hạng và ưu tiên kết quả đúng ở vị trí cao. Đồ án so sánh BM25, Semantic, "
            "Hybrid và Hybrid kết hợp Ontology trên cùng một tập câu hỏi và gold evidence.",
        ],
    ),
]

QUESTIONS = [
    ("q01", "BM25 xếp hạng đoạn văn dựa trên yếu tố nào?", 1),
    ("q02", "Hạn chế của tìm kiếm từ khóa là gì?", 1),
    ("q03", "Vector embedding được sử dụng như thế nào?", 2),
    ("q04", "Phương pháp nào tìm kiếm dựa trên ý nghĩa?", 2),
    ("q05", "RRF kết hợp các bảng xếp hạng như thế nào?", 3),
    ("q06", "Vì sao Hybrid Search kết hợp BM25 và Semantic Search?", 3),
    ("q07", "Khi nào hệ thống RAG phải từ chối trả lời?", 4),
    ("q08", "QASPER được dùng để đánh giá nội dung gì?", 5),
    ("q09", "Ontology hỗ trợ mở rộng truy vấn bằng những quan hệ nào?", 6),
    ("q10", "AI Agent làm gì trước khi tạo câu trả lời cuối cùng?", 7),
    ("q11", "Recall at k thể hiện điều gì?", 8),
    ("q12", "Chỉ số nào đánh giá vị trí của kết quả đúng đầu tiên?", 8),
]


def register_fonts() -> tuple[str, str]:
    if FONT_PATH.exists() and FONT_BOLD_PATH.exists():
        pdfmetrics.registerFont(TTFont("Arial", FONT_PATH))
        pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_BOLD_PATH))
        return "Arial", "Arial-Bold"
    return "Helvetica", "Helvetica-Bold"


def footer(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    canvas.setFont("Arial" if FONT_PATH.exists() else "Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(22 * mm, 14 * mm, "Tài liệu kiểm thử AI Agent + RAG + Ontology")
    canvas.drawRightString(188 * mm, 14 * mm, f"Trang {document.page}")
    canvas.restoreState()


def create_pdf() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    body_font, bold_font = register_fonts()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocumentTitle",
        parent=styles["Title"],
        fontName=bold_font,
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading1"],
        fontName=bold_font,
        fontSize=17,
        leading=22,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=14,
    )
    body_style = ParagraphStyle(
        "BodyVietnamese",
        parent=styles["BodyText"],
        fontName=body_font,
        fontSize=12,
        leading=18,
        alignment=0,
        textColor=colors.HexColor("#202124"),
        spaceAfter=11,
    )
    note_style = ParagraphStyle(
        "Note",
        parent=body_style,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#667085"),
        borderColor=colors.HexColor("#B8CCE4"),
        borderWidth=1,
        borderPadding=8,
        backColor=colors.HexColor("#EFF6FC"),
    )

    document = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=22 * mm,
        bottomMargin=24 * mm,
        title="Tài liệu kiểm thử Ontology-aware RAG",
        author="Trần Kim Quang",
    )
    story = []
    for index, (heading, paragraphs) in enumerate(SECTIONS):
        if index == 0:
            story.append(Paragraph("TÀI LIỆU KIỂM THỬ ONTOLOGY-AWARE RAG", title_style))
            story.append(
                Paragraph(
                    "Tài liệu tổng hợp do project tạo để kiểm tra PDF ingestion, chunking, "
                    "retrieval, query expansion, Ontology-aware re-ranking và citation. "
                    "Không sử dụng số liệu từ tài liệu này làm kết quả nghiên cứu chính thức.",
                    note_style,
                )
            )
            story.append(Spacer(1, 12 * mm))
        story.append(Paragraph(heading, heading_style))
        story.extend(Paragraph(paragraph, body_style) for paragraph in paragraphs)
        if index < len(SECTIONS) - 1:
            story.append(PageBreak())

    document.build(story, onFirstPage=footer, onLaterPages=footer)


def create_dataset() -> None:
    reader = PdfReader(PDF_PATH)
    chunks = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = " ".join((page.extract_text() or "").split())
        chunks.append(
            {
                "id": f"ontology-rag-test:p{page_number}:c1",
                "document_id": "ontology-rag-test",
                "filename": PDF_PATH.name,
                "page": page_number,
                "text": text,
            }
        )
    page_to_chunk = {chunk["page"]: chunk["id"] for chunk in chunks}
    if len(chunks) != len(SECTIONS):
        raise RuntimeError(
            f"Expected one chunk per page ({len(SECTIONS)}), but generated {len(chunks)}"
        )

    payload = {
        "description": (
            "Benchmark generated from the controlled PDF fixture. Use it for pipeline testing, "
            "not as final thesis evidence."
        ),
        "source_pdf": str(PDF_PATH.relative_to(PROJECT_ROOT)),
        "chunks": chunks,
        "questions": [
            {
                "id": question_id,
                "query": query,
                "relevant_chunk_ids": [page_to_chunk[page]],
            }
            for question_id, query, page in QUESTIONS
        ],
    }
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATASET_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    create_pdf()
    create_dataset()
    print(f"Created PDF: {PDF_PATH}")
    print(f"Created benchmark: {DATASET_PATH}")


if __name__ == "__main__":
    main()
