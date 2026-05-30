from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph import END, StateGraph

from src.agents.roles import CoordinatorAgent, ExplainerAgent, InterviewerAgent, ReviewerAgent, StudyPlannerAgent
from src.agents.state import AgentResult, AgentState
from src.agents.templates import InterviewTemplate
from src.memory.store import MemoryStore
from src.rag.indexer import VectorStore
from src.rag.retriever import format_sources, retrieve_from_store
from src.tools.registry import ToolRegistry


class AgentWorkflow:
    def __init__(
        self,
        base_dir: Path | str = ".",
        llm: Any | None = None,
        top_k: int = 4,
        config: Any | None = None,
        template: InterviewTemplate | None = None,
        store: VectorStore | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.llm = llm
        self.top_k = top_k
        self.template = template
        self.memory = MemoryStore(self.base_dir / "data" / "memory")
        self.store = store or VectorStore(
            persist_dir=self.base_dir / "data" / "vector_store",
            embedding_model=config.embedding_model if config else "",
            base_url=config.llm_base_url if config else "",
            api_key=config.llm_api_key if config else "",
        )
        font = config.pdf_font_path if config else None
        self.tools = ToolRegistry.with_defaults(self.store, self.memory, font_path=font)
        self._build_agents()

    def _build_agents(self) -> None:
        t = self.template
        self.coordinator = CoordinatorAgent(self.tools, template=t)
        self.explainer = ExplainerAgent()
        self.interviewer = InterviewerAgent(template=t)
        self.reviewer = ReviewerAgent(template=t)
        self.study_planner = StudyPlannerAgent(template=t)

    def set_template(self, template: InterviewTemplate | None) -> None:
        self.template = template
        self._build_agents()

    def run(self, question: str) -> AgentResult:
        state = AgentState(question=question)
        self._load_context(state)
        graph = self._build_graph()
        raw = graph.invoke(state)
        self._save_memory(raw)
        return AgentResult(
            answer=raw.get("answer", ""),
            sources=raw.get("sources", []),
            study_plan=raw.get("study_plan", ""),
            agent_notes=raw.get("agent_notes", {}),
        )

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)
        graph.add_node("route_task", self._route_task)
        graph.add_node("retrieve_knowledge", self._retrieve_knowledge)
        graph.add_node("collaborate", self._collaborate)
        graph.add_node("generate_answer", self._generate_answer)

        graph.set_entry_point("route_task")
        graph.add_conditional_edges(
            "route_task",
            self._after_route,
            {"retrieve": "retrieve_knowledge", "collaborate": "collaborate"},
        )
        graph.add_edge("retrieve_knowledge", "collaborate")
        graph.add_edge("collaborate", "generate_answer")
        graph.add_edge("generate_answer", END)
        return graph.compile()

    def _load_context(self, state: AgentState) -> None:
        state.profile = self.memory.get_profile()
        state.short_term_memory = self.memory.get_short_term_memory()

    def _route_task(self, state: AgentState) -> AgentState:
        route = self.coordinator.plan(state.question)
        state.agent_notes["_route"] = route
        return state

    def _after_route(self, state: AgentState) -> str:
        route = state.agent_notes.get("_route", {})
        return "retrieve" if route.get("needs_rag") else "collaborate"

    def _retrieve_knowledge(self, state: AgentState) -> AgentState:
        state.retrieved_context = retrieve_from_store(self.store, state.question, self.top_k)
        state.sources = format_sources(state.retrieved_context)
        return state

    def _collaborate(self, state: AgentState) -> AgentState:
        route = state.agent_notes.get("_route", {})
        context = "\n".join(item["text"] for item in state.retrieved_context)
        state.agent_notes["explanation"] = self.explainer.run(state.question, context)
        state.agent_notes["interview"] = self.interviewer.run(state.question, self.tools)
        state.agent_notes["review"] = self.reviewer.run(state.question)
        if route.get("needs_plan"):
            state.study_plan = self.study_planner.run(state.question, self.tools)
        return state

    def _generate_answer(self, state: AgentState) -> AgentState:
        deterministic = self.coordinator.compose(state.question, state.agent_notes, state.sources)
        if self.llm is None:
            state.answer = deterministic
            return state
        try:
            model_text = self.llm.generate(deterministic)
        except Exception:
            state.answer = deterministic
            return state
        state.answer = f"{deterministic}\n\nModel response:\n{model_text}"
        return state

    def _save_memory(self, state: dict) -> None:
        question = state.get("question", "")
        answer = state.get("answer", "")
        self.memory.add_turn("user", question)
        self.memory.add_turn("assistant", answer)
        updates: dict[str, list[str]] = {}
        lowered = question.lower()
        if "rag" in lowered:
            updates.setdefault("recent_topics", []).append("RAG")
        if "tool" in lowered or "工具" in lowered:
            updates.setdefault("recent_topics", []).append("tool calling")
        if "agent" in lowered or "智能体" in lowered:
            updates.setdefault("recent_topics", []).append("agent")
        if updates:
            self.memory.update_profile(updates)
