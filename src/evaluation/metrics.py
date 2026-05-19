from __future__ import annotations

from pathlib import Path
from typing import Any


def score_keyword_coverage(text: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    normalized = text.lower()
    hits = sum(1 for keyword in expected_keywords if keyword.lower() in normalized)
    return hits / len(expected_keywords)


def score_source_precision(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    if not retrieved_sources:
        return 0.0 if expected_sources else 1.0
    hits = sum(1 for source in retrieved_sources if _matches_any_source(source, expected_sources))
    return hits / len(retrieved_sources)


def score_source_recall(retrieved_sources: list[str], expected_sources: list[str]) -> float:
    if not expected_sources:
        return 1.0
    hits = sum(1 for expected in expected_sources if _matches_any_source(expected, retrieved_sources))
    return hits / len(expected_sources)


def score_faithfulness(answer: str, contexts: list[str], expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    grounded_text = f"{answer}\n" + "\n".join(contexts)
    return score_keyword_coverage(grounded_text, expected_keywords)


def score_tool_success_rate(expected_tools: list[str], observed_tools: list[str]) -> float:
    if not expected_tools:
        return 1.0
    hits = sum(1 for tool in expected_tools if tool in observed_tools)
    return hits / len(expected_tools)


def score_memory_hit_rate(answer: str, memory_seed: dict[str, Any]) -> float:
    expected_values = _flatten_memory_values(memory_seed)
    if not expected_values:
        return 1.0
    normalized = answer.lower()
    hits = sum(1 for value in expected_values if value.lower() in normalized)
    return hits / len(expected_values)


def score_multi_agent_completeness(answer: str, expected_sections: list[str]) -> float:
    if not expected_sections:
        return 1.0
    normalized = answer.lower()
    hits = sum(1 for section in expected_sections if section.lower() in normalized)
    return hits / len(expected_sections)


def average_scores(metrics: list[dict[str, float]]) -> dict[str, float]:
    if not metrics:
        return {}
    keys = sorted({key for item in metrics for key in item})
    return {key: sum(item.get(key, 0.0) for item in metrics) / len(metrics) for key in keys}


def _matches_any_source(source: str, candidates: list[str]) -> bool:
    source_name = Path(source).name.lower()
    source_text = source.lower()
    return any(candidate.lower() in source_text or Path(candidate).name.lower() == source_name for candidate in candidates)


def _flatten_memory_values(memory_seed: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for value in memory_seed.values():
        if isinstance(value, list):
            values.extend(str(item) for item in value if str(item))
        elif value:
            values.append(str(value))
    return values

