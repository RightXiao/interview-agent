# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup (Python 3.11+)
pip install -e ".[dev]"
cp .env.example .env  # then edit with your LLM provider details

# Run the interactive CLI
python main.py

# Run all tests (no real LLM calls needed)
python -m pytest -q

# Run a single test file
python -m pytest tests/test_commands.py -q

# Run the evaluation suite (standalone)
python -m src.evaluation.run

# Run evaluation from within the CLI
# > /eval
```

## Architecture

This is a beginner-friendly CLI agent for interview preparation. It demonstrates agent orchestration, tool calling, memory, RAG, multi-agent collaboration, PDF import, and PDF export — all locally runnable.

**Flow through the system:**

```
CLI (src/cli/app.py)
  → commands.py parses slash commands (/import, /export, /eval, etc.)
  → plain text goes to AgentWorkflow.run()
    → loads context (memory + profile)
    → CoordinatorAgent.plan() decides whether RAG/plan are needed
    → retrieve_knowledge() runs keyword-based retrieval against local JSON index
    → collaborate(): ExplainerAgent, InterviewerAgent, ReviewerAgent, (optional) StudyPlannerAgent
    → CoordinatorAgent.compose() merges sections into final answer
    → optionally calls real LLM (langchain-openai ChatOpenAI) if injected
    → saves turn to short-term memory, updates profile on keyword match
```

**Key architectural decisions:**

- The `AgentWorkflow` (src/agents/graph.py) is a procedural sequence of method calls, **not** a LangGraph StateGraph. Despite the filename and imports, LangGraph is not actually used as a graph runner — the workflow is plain Python.
- All agent roles (src/agents/roles.py) produce **deterministic** output based on keyword matching and templates. No agent calls an LLM on its own.
- The RAG retriever (src/rag/retriever.py) uses **keyword frequency scoring** (Counter-based), not embedding vectors. The "vector store" is a JSON file at `data/vector_store/local_index.json`.
- PDF import uses PyMuPDF (fitz), extracting text page-by-page with page metadata preserved for source citations.
- PDF export uses ReportLab. For Chinese text, set `PDF_FONT_PATH` in `.env` to a Chinese TTF font.
- Memory is two-layer: `data/memory/session.json` (short-term turns, capped by `MEMORY_MAX_TURNS`) and `data/memory/profile.json` (long-term user profile).

**Module boundaries:**

| Module | Responsibility |
|--------|---------------|
| `src/cli/` | Interactive loop, slash command parsing |
| `src/agents/` | Workflow execution (graph.py), agent roles (roles.py), state types (state.py) |
| `src/tools/` | Tool registry — string-keyed callables, discoverable by name |
| `src/memory/` | JSON file-based session + profile storage |
| `src/rag/` | Document chunking, JSON index build, keyword retrieval |
| `src/documents/` | md/txt/pdf loading, PDF export, data models |
| `src/llm/` | OpenAI-compatible client wrapper (lazy import of langchain-openai) |
| `src/evaluation/` | Dataset loading, metric scoring, report generation (md/json/pdf) |
| `src/config.py` | `.env` → frozen `AppConfig` dataclass |

**Test conventions:**
Tests live in `tests/` and are detected by pytest. Tests use deterministic behavior — no real LLM calls. The `AppConfig` can be constructed directly without `.env` for tests.
