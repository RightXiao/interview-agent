from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from src.documents.exporters import export_answer_to_pdf
from src.evaluation.dataset import EvaluationReport


def write_json_report(report: EvaluationReport, output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_markdown_report(report: EvaluationReport, output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Agent Evaluation Report",
        "",
        "## Summary",
        f"- Total cases: {report.total_cases}",
        f"- Passed cases: {report.passed_cases}",
        f"- Average score: {report.average_score:.2f}",
        f"- Average latency: {report.average_latency_ms:.2f} ms",
        "",
        "## Metric Averages",
    ]
    for key, value in sorted(report.metric_averages.items()):
        lines.append(f"- {key}: {value:.2f}")
    lines.extend(["", "## Case Details"])
    for case in report.cases:
        lines.extend(
            [
                "",
                f"### {case.case_id}",
                f"- Question: {case.question}",
                f"- Passed: {case.passed}",
                f"- Overall score: {case.overall_score:.2f}",
                f"- Latency: {case.latency_ms:.2f} ms",
                f"- Retrieved sources: {', '.join(case.retrieved_sources) or 'none'}",
                f"- Observed tools: {', '.join(case.observed_tools) or 'none'}",
                f"- Failure reasons: {', '.join(case.failure_reasons) or 'none'}",
                "",
                "Answer excerpt:",
                "",
                case.answer_excerpt,
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_pdf_report(report: EvaluationReport, output_path: Path | str, font_path: str | None = None) -> Path:
    summary = [
        "Agent Evaluation Report",
        "",
        f"Total cases: {report.total_cases}",
        f"Passed cases: {report.passed_cases}",
        f"Average score: {report.average_score:.2f}",
        f"Average latency: {report.average_latency_ms:.2f} ms",
        "",
        "Metric averages:",
    ]
    summary.extend(f"- {key}: {value:.2f}" for key, value in sorted(report.metric_averages.items()))
    for case in report.cases:
        summary.extend(
            [
                "",
                f"Case {case.case_id}: score={case.overall_score:.2f}, passed={case.passed}",
                f"Question: {case.question}",
                f"Sources: {', '.join(case.retrieved_sources) or 'none'}",
                f"Failures: {', '.join(case.failure_reasons) or 'none'}",
            ]
        )
    return export_answer_to_pdf(
        title="Agent Evaluation Report",
        content="\n".join(summary),
        sources=[],
        output_path=output_path,
        font_path=font_path,
    )

