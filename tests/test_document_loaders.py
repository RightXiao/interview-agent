import pytest

from src.documents.loaders import DocumentLoadError, load_document


def test_load_text_document(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("hello rag", encoding="utf-8")

    docs = load_document(path)

    assert len(docs) == 1
    assert docs[0].text == "hello rag"
    assert docs[0].source_type == "txt"


def test_load_markdown_document(tmp_path):
    path = tmp_path / "note.md"
    path.write_text("# Agent\n\nTool calling", encoding="utf-8")

    docs = load_document(path)

    assert len(docs) == 1
    assert docs[0].source_type == "md"
    assert "Tool calling" in docs[0].text


def test_reject_unsupported_file(tmp_path):
    path = tmp_path / "bad.docx"
    path.write_text("x", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        load_document(path)

