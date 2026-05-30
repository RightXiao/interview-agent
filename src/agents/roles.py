from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.templates import InterviewTemplate

if TYPE_CHECKING:
    from src.tools.registry import ToolRegistry


class CoordinatorAgent:
    def __init__(self, tools: "ToolRegistry", template: InterviewTemplate | None = None) -> None:
        self.tools = tools
        self.template = template

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
        if self.template:
            sections.extend(["", f"Target: {self.template.label}"])
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
    def __init__(self, template: InterviewTemplate | None = None) -> None:
        self.template = template

    def run(self, topic: str, tools: "ToolRegistry") -> str:
        try:
            questions = tools.call("generate_interview_questions", topic)
        except Exception:
            questions = [f"What do you know about {topic}?"]
        result = "\n".join(f"{index}. {question}" for index, question in enumerate(questions, start=1))
        if self.template and self.template.follow_up_hints:
            hints = "\n".join(f"  - {h}" for h in self.template.follow_up_hints[:3])
            result += f"\n\nLikely follow-ups ({self.template.label}):\n{hints}"
        return result


class ReviewerAgent:
    def __init__(self, template: InterviewTemplate | None = None) -> None:
        self.template = template

    def run(self, question: str) -> str:
        base = (
            "A strong interview answer should mention the business goal, the workflow, the module boundaries, "
            "failure handling, and tests. Avoid only naming frameworks; explain why each part exists."
        )
        if self.template and self.template.review_focus:
            focus = "\n".join(f"  - {f}" for f in self.template.review_focus[:3])
            base += f"\n\nKey focus for {self.template.label}:\n{focus}"
        return base


class StudyPlannerAgent:
    def __init__(self, template: InterviewTemplate | None = None) -> None:
        self.template = template

    def run(self, topic: str, tools: "ToolRegistry") -> str:
        try:
            plan = tools.call("generate_study_plan", topic)
        except Exception:
            plan = f"Study plan for {topic}\n1. Understand the core concept.\n2. Map to project modules.\n3. Prepare interview explanation.\n4. Practice follow-up questions.\n5. Review trade-offs and test strategy."
        if self.template and self.template.study_plan_extra:
            extra = "\n".join(f"  {i}. {e}" for i, e in enumerate(self.template.study_plan_extra, start=6))
            plan += f"\n\nExtra for {self.template.label}:\n{extra}"
        return plan
