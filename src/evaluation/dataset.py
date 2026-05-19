from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    question: str
    expected_keywords: list[str] = field(default_factory=list)
    expected_sources: list[str] = field(default_factory=list)
    expected_tools: list[str] = field(default_factory=list)
    expected_agent_sections: list[str] = field(default_factory=list)
    memory_seed: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    question: str
    answer_excerpt: str
    retrieved_sources: list[str]
    expected_tools: list[str]
    observed_tools: list[str]
    metrics: dict[str, float]
    latency_ms: float
    overall_score: float
    passed: bool
    failure_reasons: list[str]


@dataclass(frozen=True)
class EvaluationReport:
    total_cases: int
    passed_cases: int
    average_score: float
    average_latency_ms: float
    metric_averages: dict[str, float]
    cases: list[CaseScore]


def load_evaluation_cases(path: Path | str) -> list[EvaluationCase]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        EvaluationCase(
            id=item["id"],
            question=item["question"],
            expected_keywords=item.get("expected_keywords", []),
            expected_sources=item.get("expected_sources", []),
            expected_tools=item.get("expected_tools", []),
            expected_agent_sections=item.get("expected_agent_sections", []),
            memory_seed=item.get("memory_seed", {}),
        )
        for item in data
    ]

