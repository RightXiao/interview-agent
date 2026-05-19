from src.cli.app import CliSession


def test_cli_session_imports_document(tmp_path):
    source = tmp_path / "note.txt"
    source.write_text("RAG note", encoding="utf-8")
    session = CliSession(base_dir=tmp_path)

    result = session.handle_input(f"/import {source}")

    assert "Imported" in result

