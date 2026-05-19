# Agent Evaluation Subsystem Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local evaluation subsystem that scores the interview agent with RAGAS-style RAG metrics, Agent task metrics, latency, and report generation.

**Architecture:** Evaluation cases are loaded from JSON, executed through `AgentWorkflow`, scored by deterministic metric functions, and written as JSON, Markdown, and PDF reports. The module is independent of hosted eval services but keeps metric names aligned with RAGAS, DeepEval, and LangSmith-style evaluation.

**Tech Stack:** Python, pytest, current `AgentWorkflow`, local JSON datasets, Markdown reports, existing ReportLab PDF exporter.

---

### Task 1: Dataset and Metric Models

**Files:**
- Create: `src/evaluation/dataset.py`
- Create: `src/evaluation/metrics.py`
- Create: `src/evaluation/__init__.py`
- Test: `tests/test_evaluation_metrics.py`

- [ ] **Step 1: Write failing tests**

```python
from src.evaluation.metrics import score_keyword_coverage, score_source_precision, score_source_recall


def test_keyword_coverage_scores_expected_terms():
    score = score_keyword_coverage("RAG uses retrieval and generation", ["retrieval", "generation"])
    assert score == 1.0


def test_source_precision_and_recall_match_expected_sources():
    retrieved = ["data/knowledge_base/rag_basics.md", "data/knowledge_base/tool_calling.md"]
    expected = ["rag_basics.md"]

    assert score_source_precision(retrieved, expected) == 0.5
    assert score_source_recall(retrieved, expected) == 1.0
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_evaluation_metrics.py -q`
Expected: FAIL because evaluation modules do not exist.

- [ ] **Step 3: Implement dataset and metrics**

Implement dataclasses for `EvaluationCase`, `CaseScore`, `EvaluationReport`, plus deterministic metric helpers.

- [ ] **Step 4: Re-run tests**

Run: `python -m pytest tests/test_evaluation_metrics.py -q`
Expected: PASS.

### Task 2: Evaluation Runner and Reports

**Files:**
- Create: `src/evaluation/runner.py`
- Create: `src/evaluation/report.py`
- Create: `src/evaluation/run.py`
- Create: `evals/datasets/interview_agent_eval.json`
- Create: `evals/reports/.gitkeep`
- Test: `tests/test_evaluation_runner.py`

- [ ] **Step 1: Write failing runner tests**

```python
import json

from src.evaluation.dataset import EvaluationCase
from src.evaluation.runner import EvaluationRunner


def test_evaluation_runner_writes_reports(tmp_path):
    cases = [
        EvaluationCase(
            id="case_1",
            question="Explain RAG",
            expected_keywords=["rag"],
            expected_sources=["rag_basics.md"],
            expected_tools=["search_knowledge_base"],
            expected_agent_sections=["Explanation"],
            memory_seed={"weak_points": ["RAG"]},
        )
    ]

    runner = EvaluationRunner(base_dir=tmp_path)
    report = runner.run_cases(cases)
    paths = runner.write_reports(report)

    assert report.total_cases == 1
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    assert paths["pdf"].exists()
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_evaluation_runner.py -q`
Expected: FAIL because runner does not exist.

- [ ] **Step 3: Implement runner and report writers**

Use `AgentWorkflow`, `build_local_index`, metric functions, and existing PDF exporter.

- [ ] **Step 4: Re-run tests**

Run: `python -m pytest tests/test_evaluation_runner.py -q`
Expected: PASS.

### Task 3: CLI and Documentation

**Files:**
- Modify: `src/cli/commands.py`
- Modify: `src/cli/app.py`
- Modify: `README.md`
- Modify: `.gitignore`
- Test: `tests/test_commands.py`
- Test: `tests/test_cli_app.py`

- [ ] **Step 1: Add failing tests for `/eval`**

Add command parser and CLI session tests showing `/eval` runs the local evaluator.

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_commands.py tests/test_cli_app.py -q`
Expected: FAIL because `/eval` is not implemented.

- [ ] **Step 3: Implement `/eval` and docs**

Add `CommandType.EVAL`, CLI handler, report ignore rules, and README usage instructions.

- [ ] **Step 4: Run all tests**

Run: `python -m pytest -q`
Expected: PASS.

