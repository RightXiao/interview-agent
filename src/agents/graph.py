from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.roles import CoordinatorAgent, ExplainerAgent, InterviewerAgent, ReviewerAgent, StudyPlannerAgent
from src.agents.state import AgentResult, AgentState
from src.memory.store import MemoryStore
from src.rag.indexer import LocalKnowledgeIndex
from src.rag.retriever import format_sources, retrieve_from_local_index


class AgentWorkflow:
    def __init__(self, base_dir: Path | str = ".", llm: Any | None = None, top_k: int = 4) -> None:
        self.base_dir = Path(base_dir)
        self.llm = llm
        self.top_k = top_k
        self.memory = MemoryStore(self.base_dir / "data" / "memory")
        self.index = LocalKnowledgeIndex(self.base_dir / "data" / "vector_store" / "local_index.json")
        self.coordinator = CoordinatorAgent()
        self.explainer = ExplainerAgent()
        self.interviewer = InterviewerAgent()
        self.reviewer = ReviewerAgent()
        self.study_planner = StudyPlannerAgent()

    def run(self, question: str) -> AgentResult:
        state = AgentState(question=question)
        self._load_context(state)
        route = self.coordinator.plan(question)
        if route["needs_rag"]:
            self._retrieve_knowledge(state)
        self._collaborate(state, route)
        self._generate_answer(state)
        self._save_memory(state)
        return AgentResult(
            answer=state.answer,
            sources=state.sources,
            study_plan=state.study_plan,
            agent_notes=state.agent_notes,
        )

    def _load_context(self, state: AgentState) -> None:
        state.profile = self.memory.get_profile()
        state.short_term_memory = self.memory.get_short_term_memory()

    def _retrieve_knowledge(self, state: AgentState) -> None:
        state.retrieved_context = retrieve_from_local_index(self.index, state.question, self.top_k)
        state.sources = format_sources(state.retrieved_context)

    def _collaborate(self, state: AgentState, route: dict[str, bool]) -> None:
        context = "\n".join(item["text"] for item in state.retrieved_context)
        state.agent_notes["explanation"] = self.explainer.run(state.question, context)
        state.agent_notes["interview"] = self.interviewer.run(state.question)
        state.agent_notes["review"] = self.reviewer.run(state.question)
        if route["needs_plan"]:
            state.study_plan = self.study_planner.run(state.question)

    def _generate_answer(self, state: AgentState) -> None:
        deterministic = self.coordinator.compose(state.question, state.agent_notes, state.sources)
        if self.llm is None:
            state.answer = deterministic
            return
        try:
            model_text = self.llm.generate(deterministic)
        except Exception:
            state.answer = deterministic
            return
        state.answer = f"{deterministic}\n\nModel response:\n{model_text}"

    def _save_memory(self, state: AgentState) -> None:
        self.memory.add_turn("user", state.question)
        self.memory.add_turn("assistant", state.answer)
        updates: dict[str, list[str]] = {}
        lowered = state.question.lower()
        if "rag" in lowered:
            updates.setdefault("recent_topics", []).append("RAG")
        if "tool" in lowered or "工具" in lowered:
            updates.setdefault("recent_topics", []).append("tool calling")
        if "agent" in lowered or "智能体" in lowered:
            updates.setdefault("recent_topics", []).append("agent")
        if updates:
            self.memory.update_profile(updates)

