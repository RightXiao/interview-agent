# Agent Interview Coach CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI AI agent project for interview preparation with LangGraph-style orchestration, tools, memory, RAG, multi-agent collaboration, PDF import, and PDF export.

**Architecture:** The CLI delegates normal user questions to an agent workflow. The workflow loads memory, retrieves context, runs specialist role agents, assembles an answer, and saves memory. Local document loaders, PDF exporters, memory stores, RAG components, and tool registry are separate modules so each capability is easy to explain in interviews.

**Tech Stack:** Python 3.11+, LangGraph, LangChain, OpenAI-compatible chat API, Chroma, PyMuPDF, ReportLab, python-dotenv, pytest.

---

## File Structure

- Create `main.py`: application entry point.
- Create `pyproject.toml`: package metadata, dependencies, pytest config.
- Create `.env.example`: model and runtime config template.
- Create `README.md`: beginner setup, usage, architecture, interview talking points.
- Create `src/config.py`: config loading.
- Create `src/cli/app.py`: CLI loop and session state.
- Create `src/cli/commands.py`: slash command parsing.
- Create `src/documents/models.py`: document data models.
- Create `src/documents/loaders.py`: md/txt/pdf loading.
- Create `src/documents/exporters.py`: answer and study-plan PDF export.
- Create `src/memory/store.py`: short-term and long-term JSON memory.
- Create `src/rag/splitter.py`: deterministic text chunking.
- Create `src/rag/indexer.py`: vector index build and fallback local JSON index.
- Create `src/rag/retriever.py`: retrieval interface.
- Create `src/llm/client.py`: OpenAI-compatible client wrapper.
- Create `src/agents/state.py`: workflow state model.
- Create `src/agents/roles.py`: coordinator and specialist agents.
- Create `src/agents/graph.py`: LangGraph workflow builder with fallback runner.
- Create `src/tools/registry.py`: tool registry and default tools.
- Create `data/knowledge_base/*.md`: built-in learning documents.
- Create `tests/*`: unit tests for core behavior.

## Task 1: Project Skeleton and Config

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `src/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

```python
from src.config import AppConfig


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("LLM_MODEL", "model")
    monkeypatch.setenv("EMBEDDING_MODEL", "embed")

    config = AppConfig.from_env()

    assert config.llm_base_url == "https://api.example.com/v1"
    assert config.llm_api_key == "key"
    assert config.llm_model == "model"
    assert config.embedding_model == "embed"
    assert config.memory_max_turns == 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL because `src.config` does not exist.

- [ ] **Step 3: Implement config and project metadata**

Implement `AppConfig.from_env()` and define dependencies in `pyproject.toml`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

## Task 2: CLI Command Parser

**Files:**
- Create: `src/cli/commands.py`
- Test: `tests/test_commands.py`

- [ ] **Step 1: Write failing command parser tests**

```python
from pathlib import Path

from src.cli.commands import CommandType, parse_command


def test_parse_import_command():
    command = parse_command("/import notes/rag.pdf")
    assert command.type == CommandType.IMPORT
    assert command.args == ["notes/rag.pdf"]


def test_parse_normal_question():
    command = parse_command("Explain RAG")
    assert command.type == CommandType.QUESTION
    assert command.args == ["Explain RAG"]


def test_parse_export_answer_command():
    command = parse_command("/export answer output/a.pdf")
    assert command.type == CommandType.EXPORT_ANSWER
    assert command.args == ["output/a.pdf"]
```

- [ ] **Step 2: Run parser tests and see expected failure**

Run: `pytest tests/test_commands.py -v`
Expected: FAIL because command parser does not exist.

- [ ] **Step 3: Implement command parser**

Create `CommandType`, `ParsedCommand`, and `parse_command()`.

- [ ] **Step 4: Run parser tests**

Run: `pytest tests/test_commands.py -v`
Expected: PASS.

## Task 3: Document Loading with PDF Support

**Files:**
- Create: `src/documents/models.py`
- Create: `src/documents/loaders.py`
- Test: `tests/test_document_loaders.py`

- [ ] **Step 1: Write failing loader tests**

```python
from pathlib import Path

import pytest

from src.documents.loaders import DocumentLoadError, load_document


def test_load_text_document(tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("hello rag", encoding="utf-8")

    docs = load_document(path)

    assert len(docs) == 1
    assert docs[0].text == "hello rag"
    assert docs[0].source_type == "txt"


def test_reject_unsupported_file(tmp_path):
    path = tmp_path / "bad.docx"
    path.write_text("x", encoding="utf-8")

    with pytest.raises(DocumentLoadError):
        load_document(path)
```

- [ ] **Step 2: Run loader tests and see expected failure**

Run: `pytest tests/test_document_loaders.py -v`
Expected: FAIL because loaders do not exist.

- [ ] **Step 3: Implement loaders**

Implement md/txt loading with standard file reads. Implement PDF loading with PyMuPDF and page metadata. Raise `DocumentLoadError` for unsupported files, damaged PDFs, missing files, and scanned PDFs without extractable text.

- [ ] **Step 4: Run loader tests**

Run: `pytest tests/test_document_loaders.py -v`
Expected: PASS for local text behavior. PDF behavior is covered through interface tests and manual dependency use.

## Task 4: PDF Export

**Files:**
- Create: `src/documents/exporters.py`
- Test: `tests/test_pdf_exporters.py`

- [ ] **Step 1: Write failing exporter test**

```python
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
```

- [ ] **Step 2: Run exporter test and see expected failure**

Run: `pytest tests/test_pdf_exporters.py -v`
Expected: FAIL because exporter does not exist.

- [ ] **Step 3: Implement ReportLab exporter**

Implement answer and study plan PDF export. Create parent directories automatically and support optional TTF font registration.

- [ ] **Step 4: Run exporter tests**

Run: `pytest tests/test_pdf_exporters.py -v`
Expected: PASS.

## Task 5: Memory Store

**Files:**
- Create: `src/memory/store.py`
- Test: `tests/test_memory_store.py`

- [ ] **Step 1: Write failing memory tests**

```python
from src.memory.store import MemoryStore


def test_memory_store_keeps_recent_turns(tmp_path):
    store = MemoryStore(tmp_path, max_turns=2)

    store.add_turn("user", "one")
    store.add_turn("assistant", "two")
    store.add_turn("user", "three")

    turns = store.get_short_term_memory()
    assert [turn["content"] for turn in turns] == ["two", "three"]


def test_profile_update_merges_lists(tmp_path):
    store = MemoryStore(tmp_path)
    store.update_profile({"weak_points": ["RAG"]})
    store.update_profile({"weak_points": ["RAG", "tools"]})

    profile = store.get_profile()
    assert profile["weak_points"] == ["RAG", "tools"]
```

- [ ] **Step 2: Run memory tests and see expected failure**

Run: `pytest tests/test_memory_store.py -v`
Expected: FAIL because memory store does not exist.

- [ ] **Step 3: Implement JSON memory store**

Implement session and profile JSON files under a configurable directory.

- [ ] **Step 4: Run memory tests**

Run: `pytest tests/test_memory_store.py -v`
Expected: PASS.

## Task 6: RAG Splitter and Local Retrieval

**Files:**
- Create: `src/rag/splitter.py`
- Create: `src/rag/indexer.py`
- Create: `src/rag/retriever.py`
- Test: `tests/test_rag.py`

- [ ] **Step 1: Write failing RAG tests**

```python
from src.documents.models import LoadedDocument
from src.rag.indexer import LocalKnowledgeIndex
from src.rag.retriever import retrieve_from_local_index
from src.rag.splitter import split_documents


def test_splitter_preserves_pdf_page_metadata():
    docs = [
        LoadedDocument(
            source_path="a.pdf",
            source_type="pdf",
            text="RAG retrieves context before generation.",
            page=2,
        )
    ]

    chunks = split_documents(docs, chunk_size=20, overlap=5)

    assert chunks[0].metadata["page"] == 2
    assert chunks[0].metadata["source_type"] == "pdf"


def test_local_index_retrieves_matching_chunk(tmp_path):
    index = LocalKnowledgeIndex(tmp_path / "index.json")
    index.write([
        {
            "text": "LangGraph coordinates agent workflows.",
            "metadata": {"source_path": "agent.md", "source_type": "md", "page": None},
        }
    ])

    results = retrieve_from_local_index(index, "agent workflows", top_k=1)

    assert results[0]["metadata"]["source_path"] == "agent.md"
```

- [ ] **Step 2: Run RAG tests and see expected failure**

Run: `pytest tests/test_rag.py -v`
Expected: FAIL because RAG modules do not exist.

- [ ] **Step 3: Implement splitter, local index, and retriever**

Use a deterministic fallback JSON index so tests and demos can work without a real embedding service. Keep extension points for Chroma.

- [ ] **Step 4: Run RAG tests**

Run: `pytest tests/test_rag.py -v`
Expected: PASS.

## Task 7: Tool Registry

**Files:**
- Create: `src/tools/registry.py`
- Test: `tests/test_tool_registry.py`

- [ ] **Step 1: Write failing registry tests**

```python
from src.tools.registry import ToolRegistry


def test_tool_registry_calls_registered_tool():
    registry = ToolRegistry()
    registry.register("echo", lambda value: value)

    assert registry.call("echo", "hello") == "hello"


def test_default_tools_are_registered(tmp_path):
    registry = ToolRegistry.with_defaults(base_dir=tmp_path)

    assert registry.has("read_user_profile")
    assert registry.has("generate_study_plan")
```

- [ ] **Step 2: Run registry tests and see expected failure**

Run: `pytest tests/test_tool_registry.py -v`
Expected: FAIL because registry does not exist.

- [ ] **Step 3: Implement registry and default tools**

Implement named tool lookup and default tool wiring for memory, study plans, question generation, and PDF export.

- [ ] **Step 4: Run registry tests**

Run: `pytest tests/test_tool_registry.py -v`
Expected: PASS.

## Task 8: Agents and Workflow

**Files:**
- Create: `src/agents/state.py`
- Create: `src/agents/roles.py`
- Create: `src/agents/graph.py`
- Create: `src/llm/client.py`
- Test: `tests/test_agents.py`

- [ ] **Step 1: Write failing agent workflow tests**

```python
from src.agents.graph import AgentWorkflow


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return "fake model response"


def test_workflow_returns_answer(tmp_path):
    workflow = AgentWorkflow(base_dir=tmp_path, llm=FakeLLM())

    result = workflow.run("Explain tool calling")

    assert "tool calling" in result.answer.lower()
    assert result.answer
```

- [ ] **Step 2: Run agent tests and see expected failure**

Run: `pytest tests/test_agents.py -v`
Expected: FAIL because agents do not exist.

- [ ] **Step 3: Implement role agents and workflow fallback**

Implement deterministic role-agent behavior that can run without a real API for local tests. Keep `OpenAICompatibleClient` for real model calls.

- [ ] **Step 4: Run agent tests**

Run: `pytest tests/test_agents.py -v`
Expected: PASS.

## Task 9: CLI App and Main Entry

**Files:**
- Create: `src/cli/app.py`
- Create: `main.py`
- Test: `tests/test_cli_app.py`

- [ ] **Step 1: Write failing CLI app tests**

```python
from src.cli.commands import CommandType
from src.cli.app import CliSession


def test_cli_session_imports_document(tmp_path):
    source = tmp_path / "note.txt"
    source.write_text("RAG note", encoding="utf-8")
    session = CliSession(base_dir=tmp_path)

    result = session.handle_input(f"/import {source}")

    assert "Imported" in result
```

- [ ] **Step 2: Run CLI tests and see expected failure**

Run: `pytest tests/test_cli_app.py -v`
Expected: FAIL because CLI app does not exist.

- [ ] **Step 3: Implement CLI session and main entry**

Implement slash command handling, normal question dispatch, upload copy, reindex, memory view, clear, export answer, export plan, and exit.

- [ ] **Step 4: Run CLI tests**

Run: `pytest tests/test_cli_app.py -v`
Expected: PASS.

## Task 10: Built-in Knowledge and README

**Files:**
- Create: `data/knowledge_base/agent_basics.md`
- Create: `data/knowledge_base/rag_basics.md`
- Create: `data/knowledge_base/tool_calling.md`
- Create: `data/knowledge_base/multi_agent.md`
- Create: `data/knowledge_base/memory_design.md`
- Create: `README.md`

- [ ] **Step 1: Add built-in knowledge documents**

Write short educational Markdown files covering the core interview topics.

- [ ] **Step 2: Add README**

Include installation, `.env`, CLI commands, architecture, PDF notes, and interview talking points.

- [ ] **Step 3: Run all tests if dependencies are available**

Run: `pytest -v`
Expected: PASS if dependencies are installed. If dependency installation is not available, record that tests were not run.

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: build agent interview coach cli"
```

