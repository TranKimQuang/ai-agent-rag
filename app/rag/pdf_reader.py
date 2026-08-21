import pymupdf


class PdfReadError(ValueError):
    pass


def extract_pdf_pages(content: bytes) -> list[tuple[int, str]]:
    if not content:
        raise PdfReadError("PDF file is empty")

    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            if document.needs_pass:
                raise PdfReadError("Password-protected PDFs are not supported yet")
            return [(index + 1, page.get_text("text")) for index, page in enumerate(document)]
    except PdfReadError:
        raise
    except Exception as exc:
        raise PdfReadError("The uploaded file is not a readable PDF") from exc

