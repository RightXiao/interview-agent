from src.cli.app import CliSession


def test_cli_session_imports_document(tmp_path):
    source = tmp_path / "note.txt"
    source.write_text("RAG note", encoding="utf-8")
    session = CliSession(base_dir=tmp_path)

    result = session.handle_input(f"/import {source}")

    assert "Imported" in result


def test_cli_session_runs_evaluation(tmp_path):
    (tmp_path / "evals" / "datasets").mkdir(parents=True)
    (tmp_path / "data" / "knowledge_base").mkdir(parents=True)
    (tmp_path / "data" / "knowledge_base" / "rag_basics.md").write_text(
        "RAG uses retrieval and generation.",
        encoding="utf-8",
    )
    (tmp_path / "evals" / "datasets" / "interview_agent_eval.json").write_text(
        """[
  {
    "id": "rag_eval",
    "question": "Explain RAG",
    "expected_keywords": ["rag", "retrieval"],
    "expected_sources": ["rag_basics.md"],
    "expected_tools": ["search_knowledge_base"],
    "expected_agent_sections": ["Explanation"],
    "memory_seed": {"weak_points": ["RAG"]}
  }
]""",
        encoding="utf-8",
    )
    session = CliSession(base_dir=tmp_path)

    result = session.handle_input("/eval")

    assert "Evaluation complete" in result
