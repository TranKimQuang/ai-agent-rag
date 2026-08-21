import pymupdf

from app.rag.pdf_reader import extract_pdf_pages


def test_extract_pdf_pages() -> None:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "RAG document content")
    content = document.tobytes()
    document.close()

    pages = extract_pdf_pages(content)

    assert pages[0][0] == 1
    assert "RAG document content" in pages[0][1]
