from src.documents.exporters import export_answer_to_pdf


def test_export_answer_to_pdf_creates_file(tmp_path):
    output = tmp_path / "answer.pdf"

    result = export_answer_to_pdf(
        title="RAG Answer",
        content="RAG combines retrieval and generation.",
        sources=["notes.pdf page 2"],
        output_path=output,
        font_path=None,
    )

    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0

