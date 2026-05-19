# Agent Interview Coach CLI Requirements

## 1. Project Goal

Build a command-line AI agent project for interview preparation and learning. The project is designed for beginners who need a complete but understandable example that covers:

- agent framework orchestration
- tool calling
- memory
- RAG
- multi-agent collaboration
- PDF import and PDF export

The first version should be useful as both a learning project and an interview portfolio project.

## 2. Target Users

Primary user:

- A beginner learning AI agent engineering.
- A developer preparing for AI agent, RAG, Python, backend, or LLM application interviews.

Secondary user:

- An interviewer or reviewer who wants to inspect a clear, locally runnable agent project.

## 3. Product Form

The first version is a Python command-line application.

The user runs:

```bash
python main.py
```

Then the user enters an interactive CLI session with normal conversation and slash commands.

## 4. Core Capabilities

### 4.1 Agent Framework

The project must use Python with LangGraph and LangChain.

LangGraph is responsible for workflow orchestration. LangChain components are used for LLM calls, document handling, tool wrapping, embeddings, and vector retrieval where appropriate.

### 4.2 LLM Provider

The project must support OpenAI-compatible domestic model APIs.

Configuration must be provided through environment variables:

```text
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
EMBEDDING_MODEL
```

The code must avoid hard-coding a single provider.

### 4.3 RAG System

The project must support both built-in documents and user-imported files.

Supported import formats for version 1:

- Markdown: `.md`
- Text: `.txt`
- PDF: `.pdf`

PDF import must:

- extract text page by page
- preserve page numbers in metadata
- reject empty or scanned PDFs with a clear message
- handle damaged PDFs gracefully
- store extracted content in the vector index
- show PDF file name and page number in answer sources

### 4.4 PDF Export

The project must export generated content to PDF.

Supported export targets for version 1:

- last answer
- generated interview questions
- generated study plan

PDF export must include:

- title
- generated time
- structured body
- bullet lists when needed
- source references when available
- basic Chinese text support through configurable font path

### 4.5 Tool Calling

The agent must use a tool registry. Version 1 tools:

- search knowledge base
- read user profile
- update user profile
- generate interview questions
- generate study plan
- export last answer to PDF
- export study plan to PDF

### 4.6 Memory

The project must provide two memory layers:

- short-term session memory
- long-term user profile memory

Short-term memory stores recent conversation turns.

Long-term memory stores stable user information:

- target role
- preferred tech stack
- weak points
- learning goals
- recent topics

Long-term memory should be updated only when there is a clear new preference, goal, weak point, or learning topic.

### 4.7 Multi-Agent Collaboration

The first version must include at least four roles:

- CoordinatorAgent: routes and coordinates work
- ExplainerAgent: explains concepts
- InterviewerAgent: generates interview questions and follow-ups
- ReviewerAgent: evaluates answers and gives improvement advice

The collaboration model is centralized: the coordinator calls specialist agents and merges their outputs.

### 4.8 CLI Commands

The CLI must support:

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
/exit
```

Normal text input is treated as a user question.

## 5. Out of Scope for Version 1

- Web frontend
- REST API service
- user account system
- cloud database
- OCR for scanned PDFs
- Word document import
- spreadsheet import
- web crawler
- model fine-tuning
- production observability
- distributed deployment

## 6. Non-Functional Requirements

The project must be:

- beginner friendly
- interview friendly
- modular
- locally runnable
- easy to explain
- easy to extend into a Web or API project later

The code should prefer clear module boundaries over clever abstractions.

## 7. Acceptance Criteria

The project is accepted when:

- a user can start the CLI
- a user can ask questions in continuous conversation
- a user can import `.md`, `.txt`, and `.pdf` files
- imported PDF content can be included in RAG results with page references
- the system can export answers and study plans to PDF
- the system can read and update long-term user profile memory
- the system can show short-term conversation memory
- the tool registry can call registered tools by name
- the workflow demonstrates multi-agent collaboration
- README explains setup, usage, architecture, and interview talking points

