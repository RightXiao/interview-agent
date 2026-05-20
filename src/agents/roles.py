from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.tools.registry import ToolRegistry


class CoordinatorAgent:
    def __init__(self, tools: "ToolRegistry") -> None:
        self.tools = tools

    def plan(self, question: str) -> dict[str, bool]:
        text = question.lower()
        return {
            "needs_rag": self.tools.has("search_knowledge_base"),
            "needs_interview": any(keyword in text for keyword in ["interview", "面试", "question", "题"]),
            "needs_plan": any(keyword in text for keyword in ["plan", "学习", "study", "准备"]),
        }

    def compose(self, question: str, notes: dict[str, str], sources: list[str]) -> str:
        sections = [
            f"Question: {question}",
            "",
            "Explanation:",
            notes.get("explanation", ""),
            "",
            "Interview follow-ups:",
            notes.get("interview", ""),
            "",
            "Review advice:",
            notes.get("review", ""),
        ]
        if sources:
            sections.extend(["", "Sources:", *[f"- {source}" for source in sources]])
        return "\n".join(section for section in sections if section is not None)


class ExplainerAgent:
    def run(self, question: str, context: str = "") -> str:
        context_line = f" Based on retrieved context: {context[:300]}" if context else ""
        return (
            f"{question} can be explained through project structure, data flow, and trade-offs."
            f"{context_line} In this project, the implementation should be mapped to clear modules so it is easy to discuss in an interview."
        )


class InterviewerAgent:
    def run(self, topic: str, tools: "ToolRegistry") -> str:
        try:
            questions = tools.call("generate_interview_questions", topic)
        except Exception:
            questions = [f"What do you know about {topic}?"]
        return "\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1))


class ReviewerAgent:
    def run(self, question: str) -> str:
        return (
            "A strong interview answer should mention the business goal, the workflow, the module boundaries, "
            "failure handling, and tests. Avoid only naming frameworks; explain why each part exists."
        )


class StudyPlannerAgent:
    def run(self, topic: str, tools: "ToolRegistry") -> str:
        try:
            return tools.call("generate_study_plan", topic)
        except Exception:
            return f"Study plan for {topic}\n1. Understand the core concept.\n2. Map to project modules.\n3. Prepare interview explanation.\n4. Practice follow-up questions.\n5. Review trade-offs and test strategy."
