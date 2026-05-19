from __future__ import annotations

from src.tools.registry import generate_interview_questions, generate_study_plan


class CoordinatorAgent:
    def plan(self, question: str) -> dict[str, bool]:
        text = question.lower()
        return {
            "needs_rag": True,
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
    def run(self, topic: str) -> str:
        return "\n".join(f"{index}. {question}" for index, question in enumerate(generate_interview_questions(topic), start=1))


class ReviewerAgent:
    def run(self, question: str) -> str:
        return (
            "A strong interview answer should mention the business goal, the workflow, the module boundaries, "
            "failure handling, and tests. Avoid only naming frameworks; explain why each part exists."
        )


class StudyPlannerAgent:
    def run(self, topic: str) -> str:
        return generate_study_plan(topic)

