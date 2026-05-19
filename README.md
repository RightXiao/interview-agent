# Agent Interview Coach CLI

A beginner-friendly command-line AI agent project for interview preparation. It demonstrates agent orchestration, tool calling, memory, RAG, multi-agent collaboration, PDF import, and PDF export.

## What This Project Shows

- LangGraph/LangChain-oriented agent architecture
- OpenAI-compatible domestic model API configuration
- Local RAG over built-in and imported documents
- PDF import with page metadata
- PDF export for answers and study plans
- Short-term and long-term memory
- Centralized multi-agent collaboration
- Testable module boundaries

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Edit `.env`:

```text
LLM_BASE_URL=https://your-provider.example.com/v1
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=your-chat-model
EMBEDDING_MODEL=your-embedding-model
PDF_FONT_PATH=
```

For Chinese PDF export, set `PDF_FONT_PATH` to a local Chinese `.ttf` font.

## Run

```bash
python main.py
```

Commands:

```text
/help
/import path/to/file.md
/import path/to/file.txt
/import path/to/file.pdf
/memory
/reindex
/clear
/export answer output/answer.pdf
/export plan output/study_plan.pdf
/eval
/exit
```

Normal text input is sent to the agent workflow.

## PDF Notes

PDF import uses PyMuPDF. It extracts text page by page and stores page numbers as RAG metadata.

Scanned PDFs are not supported in version 1 because they need OCR. If a PDF has no extractable text, the CLI returns a clear error.

PDF export uses ReportLab and creates readable text PDFs for answers and study plans.

## Architecture

```text
CLI
  -> command parser
  -> agent workflow
  -> memory store
  -> local RAG retriever
  -> tool registry
  -> specialist agents
  -> answer and optional PDF export
```

Important modules:

- `src/cli`: command loop and slash commands
- `src/agents`: workflow and agent roles
- `src/tools`: tool registry
- `src/memory`: JSON memory
- `src/rag`: chunking, indexing, retrieval
- `src/documents`: md/txt/pdf loading and PDF export
- `src/llm`: OpenAI-compatible client wrapper

## Interview Talking Points

1. The workflow is explicit: load context, retrieve knowledge, collaborate, answer, save memory.
2. Tools are registered by name, which makes tool calling inspectable and testable.
3. RAG keeps metadata, including PDF page numbers, so answers can cite sources.
4. Memory is split into short-term conversation and long-term user profile.
5. Multi-agent collaboration is centralized for clarity and testability.
6. The first version avoids accounts, web UI, OCR, and cloud databases so the core agent concepts stay visible.

## Tests

```bash
python -m pytest -q
```

The tests are designed to avoid real LLM calls.

## Evaluation

Run the local evaluation suite:

```bash
python -m src.evaluation.run
```

Or from the interactive CLI:

```text
/eval
```

Reports are written to:

```text
evals/reports/eval_report.md
evals/reports/eval_report.json
evals/reports/eval_report.pdf
```

The default evaluator uses deterministic local metrics aligned with mainstream evaluation dimensions:

- RAGAS-style RAG metrics: answer relevancy, faithfulness, context precision, context recall.
- DeepEval-style agent/task metrics: tool success, memory hit rate, multi-agent completeness.
- LangSmith-style experiment structure: dataset cases, repeated execution, per-case report output.

This keeps the first version locally runnable and interview-friendly while leaving room to integrate official hosted or LLM-judge evaluators later.

