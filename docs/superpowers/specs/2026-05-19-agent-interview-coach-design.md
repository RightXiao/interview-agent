# Agent Interview Coach CLI Spec

## Confirmed Scope

Build a Python command-line AI agent project for interview preparation. The project must be beginner friendly and cover agent framework orchestration, tool calling, memory, RAG, multi-agent collaboration, PDF import, and PDF export.

## Confirmed Choices

- Product form: CLI application.
- Tech stack: Python, LangGraph, LangChain.
- LLM provider: domestic OpenAI-compatible API, configured through `.env`.
- RAG sources: built-in documents and user imports.
- Import formats: `.md`, `.txt`, `.pdf`.
- Export formats: PDF for answers and study plans.
- Memory: short-term conversation memory and long-term user profile.
- Multi-agent pattern: centralized coordinator with specialist role agents.

## Requirements

See `docs/requirements.md`.

## Design

See `docs/design.md`.

## Implementation Notes

The first implementation should keep the system modular and easy to explain. It should avoid production-level complexity such as user accounts, web frontend, OCR, cloud databases, and distributed deployment.

PDF support is part of version 1. PDF import must preserve page metadata for RAG references. PDF export must support readable text output and configurable Chinese font support.

## Acceptance Criteria

- CLI starts through `python main.py`.
- `/import` accepts `.md`, `.txt`, and `.pdf`.
- PDF import extracts text and stores page metadata.
- `/reindex` rebuilds local vector data from built-in and uploaded documents.
- Normal user questions flow through the agent workflow.
- Answers can include RAG sources.
- `/memory` shows short-term and long-term memory.
- `/export answer` creates a PDF from the last answer.
- `/export plan` creates a PDF from the latest study plan.
- README explains setup, usage, architecture, and interview talking points.

