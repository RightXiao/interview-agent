from __future__ import annotations

from pathlib import Path

from src.documents.models import LoadedDocument


class DocumentLoadError(RuntimeError):
    """Raised when a document cannot be loaded into the RAG pipeline."""


def load_document(path: Path | str) -> list[LoadedDocument]:
    file_path = Path(path)
    if not file_path.exists():
        raise DocumentLoadError(f"File does not exist: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".md":
        return [_load_text_like(file_path, "md")]
    if suffix == ".txt":
        return [_load_text_like(file_path, "txt")]
    if suffix == ".pdf":
        return _load_pdf(file_path)
    raise DocumentLoadError("Unsupported file type. Version 1 supports .md, .txt, and .pdf.")


def _load_text_like(path: Path, source_type: str) -> LoadedDocument:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentLoadError(f"File must be UTF-8 encoded: {path}") from exc
    return LoadedDocument(source_path=str(path), source_type=source_type, text=text)


def _load_pdf(path: Path) -> list[LoadedDocument]:
    try:
        import fitz
    except ImportError as exc:
        raise DocumentLoadError("PyMuPDF is required for PDF import. Install dependency: pymupdf") from exc

    try:
        pdf = fitz.open(path)
    except Exception as exc:
        raise DocumentLoadError(f"Failed to open PDF: {path}") from exc

    documents: list[LoadedDocument] = []
    try:
        for index, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:
                documents.append(
                    LoadedDocument(
                        source_path=str(path),
                        source_type="pdf",
                        text=text,
                        page=index,
                    )
                )
    finally:
        pdf.close()

    if not documents:
        raise DocumentLoadError("No extractable text found. This may be a scanned PDF; OCR is not supported in version 1.")
    return documents

