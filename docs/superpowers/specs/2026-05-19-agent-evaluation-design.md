# Agent Evaluation Subsystem Spec

## Goal

Add a local evaluation subsystem that measures the interview agent with mainstream evaluation dimensions and outputs Markdown, JSON, and PDF reports.

## Scope

Version 1 evaluates:

- RAG answer quality with RAGAS-style dimensions.
- Agent behavior with DeepEval/LangSmith-style task dimensions.
- Runtime performance through per-case latency and aggregate latency.

The subsystem must run locally without a hosted evaluation platform. It should not require a real LLM judge for the default test path.

## Benchmark Alignment

The metric names and meanings align with common LLM application evaluation practice:

- RAGAS-style RAG metrics: answer relevancy, faithfulness, context precision, context recall.
- DeepEval-style task metrics: task success, tool correctness, contextual correctness.
- LangSmith-style experiment structure: dataset cases, repeated runner execution, structured per-case reports.

Version 1 implements deterministic local metrics so the project remains beginner friendly and testable. Later versions may wrap official RAGAS, DeepEval, or LangSmith evaluators.

## Commands

Default command:

```bash
python -m src.evaluation.run
```

Optional CLI command:

```text
/eval
```

## Files

Create:

```text
evals/datasets/interview_agent_eval.json
evals/reports/.gitkeep
src/evaluation/__init__.py
src/evaluation/dataset.py
src/evaluation/metrics.py
src/evaluation/runner.py
src/evaluation/report.py
src/evaluation/run.py
tests/test_evaluation_metrics.py
tests/test_evaluation_runner.py
```

Modify:

```text
README.md
src/cli/app.py
src/cli/commands.py
.gitignore
```

## Dataset Format

Each case contains:

```json
{
  "id": "rag_001",
  "question": "What is RAG?",
  "expected_keywords": ["retrieval", "generation", "knowledge"],
  "expected_sources": ["rag_basics.md"],
  "expected_tools": ["search_knowledge_base"],
  "expected_agent_sections": ["Explanation", "Interview follow-ups", "Review advice"],
  "memory_seed": {
    "target_role": "AI Agent Engineer",
    "weak_points": ["RAG"]
  }
}
```

## Metrics

All score metrics return values between 0 and 1.

- `answer_relevancy`: overlap between answer text and expected keywords.
- `context_precision`: ratio of retrieved sources matching expected sources.
- `context_recall`: ratio of expected sources found in retrieved sources.
- `faithfulness`: ratio of expected keywords grounded in retrieved context or answer sources.
- `tool_success_rate`: ratio of expected tools whose observable effects appear in the run.
- `memory_hit_rate`: ratio of memory seed values reflected in the answer.
- `multi_agent_completeness`: ratio of expected output sections present in the answer.
- `overall_score`: average of all score metrics except latency.
- `latency_ms`: wall-clock runtime per case.
- `case_passed`: true when `overall_score >= 0.7`.

## Reports

The runner writes:

```text
evals/reports/eval_report.json
evals/reports/eval_report.md
evals/reports/eval_report.pdf
```

Markdown report sections:

- Summary
- Metric Averages
- Case Details
- Failure Reasons

JSON report keeps full per-case data.

PDF report reuses `src.documents.exporters.export_answer_to_pdf`.

## Acceptance Criteria

- `python -m src.evaluation.run` produces JSON, Markdown, and PDF reports.
- `/eval` produces the same report set from the interactive CLI.
- The default dataset includes RAG, tool, memory, and multi-agent cases.
- Unit tests cover metric calculations and runner report generation.
- Existing tests continue to pass.

