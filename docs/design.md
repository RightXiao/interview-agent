# Agent Interview Coach CLI Design

## 1. Overview

Agent Interview Coach CLI is a local command-line AI agent application. It uses LangGraph for workflow orchestration, LangChain-compatible components for LLM and retrieval operations, local JSON files for memory, and a local vector store for RAG.

High-level flow:

```text
user input
  -> CLI
  -> command parser or agent workflow
  -> context loading
  -> task routing
  -> RAG/tool calls when needed
  -> specialist agent collaboration
  -> final answer
  -> memory update
```

## 2. Proposed File Structure

```text
.
├── main.py
├── pyproject.toml
├── README.md
├── .env.example
├── src/
│   ├── agents/
│   │   ├── graph.py
│   │   ├── roles.py
│   │   └── state.py
│   ├── cli/
│   │   ├── app.py
│   │   └── commands.py
│   ├── config.py
│   ├── documents/
│   │   ├── exporters.py
│   │   ├── loaders.py
│   │   └── models.py
│   ├── llm/
│   │   └── client.py
│   ├── memory/
│   │   └── store.py
│   ├── rag/
│   │   ├── indexer.py
│   │   ├── retriever.py
│   │   └── splitter.py
│   └── tools/
│       └── registry.py
├── data/
│   ├── knowledge_base/
│   ├── memory/
│   ├── uploads/
│   └── vector_store/
├── output/
└── tests/
```

## 3. Configuration

`src/config.py` loads `.env` values into an application config object.

Required LLM settings:

```text
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
EMBEDDING_MODEL
```

Useful defaults:

```text
MEMORY_MAX_TURNS=8
RAG_TOP_K=4
PDF_FONT_PATH=
```

If `PDF_FONT_PATH` is empty, the exporter uses a built-in ReportLab font. If Chinese output is needed, the user should configure a local Chinese TTF font.

## 4. CLI Design

`src/cli/app.py` owns the interactive loop.

`src/cli/commands.py` parses slash commands:

```text
/help
/import <path>
/memory
/reindex
/clear
/export answer <output_path>
/export plan <output_path>
/exit
```

If the input does not start with `/`, it is sent to the LangGraph workflow as a normal question.

The CLI stores the latest answer and latest generated study plan in session state so PDF export commands can reuse them.

## 5. Document Loading

`src/documents/loaders.py` provides a single entry point:

```python
load_document(path: Path) -> list[LoadedDocument]
```

Supported loaders:

- Markdown loader
- text loader
- PDF loader

`LoadedDocument` contains:

```python
source_path: str
source_type: str
text: str
page: int | None
```

PDF loading uses PyMuPDF. It extracts each page separately. Pages with empty text are skipped. If all pages are empty, the loader raises a clear error explaining that OCR is not supported in version 1.

## 6. PDF Export

`src/documents/exporters.py` exports answers and study plans with ReportLab.

Exporter responsibilities:

- create output directories
- configure optional Chinese font
- write title, timestamp, body, and source list
- wrap long text
- return the generated output path

The first version does not attempt rich Markdown rendering. It focuses on reliable readable PDFs.

## 7. RAG Design

`src/rag/indexer.py` builds the vector index from:

- `data/knowledge_base`
- `data/uploads`

The indexer:

1. loads documents
2. splits text into chunks
3. attaches source metadata
4. creates embeddings
5. writes the local vector store

Chunk metadata:

```json
{
  "source_path": "data/uploads/rag_notes.pdf",
  "source_type": "pdf",
  "page": 3,
  "chunk_id": "rag_notes.pdf:p3:c2"
}
```

`src/rag/retriever.py` retrieves top-k chunks and returns text plus metadata.

The first version may use Chroma as the local vector store because it is easy to persist and common in LangChain examples.

## 8. Memory Design

`src/memory/store.py` stores memory in JSON files:

```text
data/memory/session.json
data/memory/profile.json
```

Short-term memory schema:

```json
{
  "turns": [
    {
      "role": "user",
      "content": "What is RAG?"
    },
    {
      "role": "assistant",
      "content": "RAG means retrieval augmented generation..."
    }
  ]
}
```

Long-term profile schema:

```json
{
  "target_role": "AI Agent Engineer",
  "tech_stack": ["Python", "LangGraph", "RAG"],
  "weak_points": ["vector database"],
  "learning_goals": ["prepare for agent project interview"],
  "recent_topics": ["RAG design"]
}
```

## 9. Agent Workflow

`src/agents/state.py` defines workflow state:

```python
question
profile
short_term_memory
retrieved_context
agent_notes
answer
sources
study_plan
```

`src/agents/graph.py` defines nodes:

- load_context
- route_task
- retrieve_knowledge
- collaborate_agents
- generate_answer
- save_memory

## 10. Agent Roles

`src/agents/roles.py` defines:

- CoordinatorAgent
- ExplainerAgent
- InterviewerAgent
- ReviewerAgent

The coordinator is responsible for orchestration. Specialist agents return structured text sections. The final answer is assembled by the coordinator.

## 11. Tool Registry

`src/tools/registry.py` registers callable tools:

- search_knowledge_base
- read_user_profile
- update_user_profile
- generate_interview_questions
- generate_study_plan
- export_last_answer_to_pdf
- export_study_plan_to_pdf

The registry gives the project a visible tool-calling layer for interview explanation.

## 12. Error Handling

The CLI must show clear messages for:

- missing `.env`
- missing API key
- bad model endpoint
- unsupported file type
- missing import file
- damaged PDF
- scanned PDF without extractable text
- empty vector store
- failed PDF export

## 13. Testing Strategy

Tests should use local deterministic behavior where possible.

Main test areas:

- config loading
- command parsing
- document loading for md/txt/pdf
- PDF export
- memory read/write
- text splitting
- tool registry lookup
- agent workflow with fake LLM responses

The tests should not require a real LLM API key.

## 14. Interview Talking Points

This project can be explained in interviews through five layers:

1. LangGraph workflow shows agent orchestration.
2. Tool registry shows tool calling.
3. JSON memory shows short-term and long-term memory.
4. Chroma retrieval shows RAG.
5. Role agents show multi-agent collaboration.

The PDF import and export features show the project handles realistic local documents, not only toy Markdown examples.

