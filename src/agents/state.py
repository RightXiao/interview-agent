from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    answer: str
    sources: list[str] = field(default_factory=list)
    study_plan: str = ""
    agent_notes: dict[str, str] = field(default_factory=dict)


@dataclass
class AgentState:
    question: str
    profile: dict[str, Any] = field(default_factory=dict)
    short_term_memory: list[dict[str, str]] = field(default_factory=list)
    retrieved_context: list[dict] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    agent_notes: dict[str, str] = field(default_factory=dict)
    answer: str = ""
    study_plan: str = ""

