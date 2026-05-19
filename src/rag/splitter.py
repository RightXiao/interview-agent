from __future__ import annotations

from src.documents.models import LoadedDocument, TextChunk


def split_documents(
    documents: list[LoadedDocument],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks: list[TextChunk] = []
    for document in documents:
        text = " ".join(document.text.split())
        if not text:
            continue
        start = 0
        part = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append(
                TextChunk(
                    text=chunk_text,
                    metadata={
                        "source_path": document.source_path,
                        "source_type": document.source_type,
                        "page": document.page,
                        "chunk_id": _chunk_id(document, part),
                    },
                )
            )
            if end == len(text):
                break
            start = end - overlap
            part += 1
    return chunks


def _chunk_id(document: LoadedDocument, part: int) -> str:
    page = f"p{document.page}" if document.page is not None else "p0"
    return f"{document.source_path}:{page}:c{part}"

