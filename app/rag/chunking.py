import re
from collections.abc import Iterable

from app.models import Chunk

_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse PDF line breaks and repeated whitespace into readable text."""
    return _WHITESPACE.sub(" ", text).strip()


def chunk_pages(
    pages: Iterable[tuple[int, str]],
    *,
    document_id: str,
    filename: str,
    chunk_size: int = 180,
    overlap: int = 40,
) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size")

    chunks: list[Chunk] = []
    step = chunk_size - overlap

    for page_number, raw_text in pages:
        words = normalize_text(raw_text).split()
        for start in range(0, len(words), step):
            window = words[start : start + chunk_size]
            if not window:
                continue
            chunks.append(
                Chunk(
                    id=f"{document_id}:p{page_number}:c{start // step + 1}",
                    document_id=document_id,
                    filename=filename,
                    page=page_number,
                    text=" ".join(window),
                )
            )
            if start + chunk_size >= len(words):
                break

    return chunks

