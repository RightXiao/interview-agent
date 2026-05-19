from __future__ import annotations

import time
from pathlib import Path

from src.agents.graph import AgentWorkflow
from src.evaluation.dataset import CaseScore, EvaluationCase, EvaluationReport
from src.evaluation.metrics import (
    average_scores,
    score_faithfulness,
    score_keyword_coverage,
    score_memory_hit_rate,
    score_multi_agent_completeness,
    score_source_precision,
    score_source_recall,
    score_tool_success_rate,
)
from src.evaluation.report import write_json_report, write_markdown_report, write_pdf_report
from src.rag.indexer import build_local_index


class EvaluationRunner:
    def __init__(self, base_dir: Path | str = ".", report_dir: Path | str | None = None, threshold: float = 0.7) -> None:
        self.base_dir = Path(base_dir)
        self.report_dir = Path(report_dir) if report_dir else self.base_dir / "evals" / "reports"
        self.threshold = threshold

    def run_cases(self, cases: list[EvaluationCase]) -> EvaluationReport:
        self._prepare_index()
        scores = [self._run_case(case) for case in cases]
        metric_averages = average_scores([score.metrics for score in scores])
        total = len(scores)
        passed = sum(1 for score in scores if score.passed)
        average_score = sum(score.overall_score for score in scores) / total if total else 0.0
        average_latency = sum(score.latency_ms for score in scores) / total if total else 0.0
        return EvaluationReport(
            total_cases=total,
            passed_cases=passed,
            average_score=average_score,
            average_latency_ms=average_latency,
            metric_averages=metric_averages,
            cases=scores,
        )

    def write_reports(self, report: EvaluationReport) -> dict[str, Path]:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        return {
            "json": write_json_report(report, self.report_dir / "eval_report.json"),
            "markdown": write_markdown_report(report, self.report_dir / "eval_report.md"),
            "pdf": write_pdf_report(report, self.report_dir / "eval_report.pdf"),
        }

    def _prepare_index(self) -> None:
        build_local_index(
            [self.base_dir / "data" / "knowledge_base", self.base_dir / "data" / "uploads"],
            self.base_dir / "data" / "vector_store" / "local_index.json",
        )

    def _run_case(self, case: EvaluationCase) -> CaseScore:
        workflow = AgentWorkflow(base_dir=self.base_dir)
        if case.memory_seed:
            workflow.memory.update_profile(case.memory_seed)

        started = time.perf_counter()
        result = workflow.run(case.question)
        latency_ms = (time.perf_counter() - started) * 1000

        observed_tools = self._observed_tools(case, result.sources)
        contexts = [item["text"] for item in workflow.index.read()]
        metrics = {
            "answer_relevancy": score_keyword_coverage(result.answer, case.expected_keywords),
            "context_precision": score_source_precision(result.sources, case.expected_sources),
            "context_recall": score_source_recall(result.sources, case.expected_sources),
            "faithfulness": score_faithfulness(result.answer, contexts, case.expected_keywords),
            "tool_success_rate": score_tool_success_rate(case.expected_tools, observed_tools),
            "memory_hit_rate": score_memory_hit_rate(result.answer, case.memory_seed),
            "multi_agent_completeness": score_multi_agent_completeness(result.answer, case.expected_agent_sections),
        }
        overall = sum(metrics.values()) / len(metrics)
        failures = [key for key, value in metrics.items() if value < self.threshold]
        return CaseScore(
            case_id=case.id,
            question=case.question,
            answer_excerpt=result.answer[:500],
            retrieved_sources=result.sources,
            expected_tools=case.expected_tools,
            observed_tools=observed_tools,
            metrics=metrics,
            latency_ms=latency_ms,
            overall_score=overall,
            passed=overall >= self.threshold,
            failure_reasons=failures,
        )

    def _observed_tools(self, case: EvaluationCase, sources: list[str]) -> list[str]:
        observed = []
        if sources:
            observed.append("search_knowledge_base")
        if case.memory_seed:
            observed.extend(["read_user_profile", "update_user_profile"])
        return observed

