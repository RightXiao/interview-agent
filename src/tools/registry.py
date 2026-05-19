from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.documents.exporters import export_answer_to_pdf, export_study_plan_to_pdf
from src.memory.store import MemoryStore
from src.rag.indexer import LocalKnowledgeIndex
from src.rag.retriever import format_sources, retrieve_from_local_index


class ToolNotFoundError(KeyError):
    """Raised when an agent calls an unknown tool."""


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]) -> None:
        self._tools[name] = func

    def has(self, name: str) -> bool:
        return name in self._tools

    def call(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise ToolNotFoundError(name)
        return self._tools[name](*args, **kwargs)

    @classmethod
    def with_defaults(cls, base_dir: Path | str = ".", font_path: str | None = None) -> "ToolRegistry":
        base = Path(base_dir)
        memory = MemoryStore(base / "data" / "memory")
        index = LocalKnowledgeIndex(base / "data" / "vector_store" / "local_index.json")
        registry = cls()

        registry.register("read_user_profile", memory.get_profile)
        registry.register("update_user_profile", memory.update_profile)
        registry.register("generate_interview_questions", generate_interview_questions)
        registry.register("generate_study_plan", generate_study_plan)
        registry.register("search_knowledge_base", lambda query, top_k=4: retrieve_from_local_index(index, query, top_k))
        registry.register(
            "export_last_answer_to_pdf",
            lambda title, content, sources, output_path: export_answer_to_pdf(title, content, sources, output_path, font_path),
        )
        registry.register(
            "export_study_plan_to_pdf",
            lambda plan, output_path: export_study_plan_to_pdf(plan, output_path, font_path),
        )
        return registry


def generate_interview_questions(topic: str, count: int = 5) -> list[str]:
    return [
        f"How would you explain {topic} in a project interview?",
        f"What are the core components of {topic}?",
        f"What trade-offs did you consider when implementing {topic}?",
        f"How would you test {topic}?",
        f"How would you extend {topic} for production?",
    ][:count]


def generate_study_plan(topic: str) -> str:
    return (
        f"Study plan for {topic}\n"
        "1. Understand the core concept and key terms.\n"
        "2. Map the concept to this project's modules.\n"
        "3. Prepare a two-minute interview explanation.\n"
        "4. Practice common follow-up questions.\n"
        "5. Review implementation trade-offs and test strategy."
    )


def summarize_search_results(results: list[dict]) -> str:
    if not results:
        return "No knowledge-base context was found."
    sources = format_sources(results)
    snippets = "\n".join(f"- {item['text'][:220]}" for item in results)
    return f"Retrieved context:\n{snippets}\nSources: {', '.join(sources)}"

