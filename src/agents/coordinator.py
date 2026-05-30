"""主 Agent - 负责任务分析、路由决策、结果汇总"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class CoordinatorAgent(BaseAgent):
    """主 Agent：分析意图、决定是否用 RAG、派发任务、汇总结果"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="coordinator", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行任务：分析问题并返回路由决策"""
        question = task.get("question", "")
        return self.analyze_intent(question)

    def analyze_intent(self, question: str) -> dict[str, Any]:
        """分析用户意图，决定需要哪些 Agent 参与"""
        # 尝试用 LLM 分析
        llm_result = self._llm_analyze(question)
        if llm_result:
            return llm_result

        # 回退到关键词匹配
        return self._keyword_analyze(question)

    def _llm_analyze(self, question: str) -> dict[str, Any] | None:
        """用 LLM 分析意图"""
        if not self.llm:
            return None

        prompt = f"""分析以下面试相关问题，判断需要哪些处理步骤。

问题：{question}

请返回 JSON 格式：
{{
  "needs_rag": true/false,
  "needs_preparation": true/false,
  "needs_interview": true/false,
  "needs_review": true/false,
  "phase": "preparation/interview/review/general",
  "topic": "提取的主题关键词"
}}

只返回 JSON，不要其他内容。"""

        response = self.call_llm(prompt)
        if not response:
            return None

        try:
            import json
            result = json.loads(response)
            result["topic"] = result.get("topic", question)
            return result
        except (json.JSONDecodeError, KeyError):
            return None

    def _keyword_analyze(self, question: str) -> dict[str, Any]:
        """关键词匹配分析"""
        text = question.lower()

        needs_rag = any(kw in text for kw in [
            "rag", "检索", "知识库", "文档", "向量", "embedding",
            "chroma", "索引", "search", "retrieve"
        ])

        needs_preparation = any(kw in text for kw in [
            "准备", "准备面试", "preparation", "如何准备",
            "面试前", "简历", "resume", "background"
        ])

        needs_interview = any(kw in text for kw in [
            "面试", "问题", "回答", "interview", "question",
            "追问", "follow", "how", "what", "why"
        ])

        needs_review = any(kw in text for kw in [
            "评审", "总结", "review", "改进",
            "学习计划", "study", "plan", "feedback"
        ])

        if not any([needs_preparation, needs_interview, needs_review]):
            needs_interview = True

        topic = self._extract_topic(question)

        return {
            "needs_rag": needs_rag,
            "needs_preparation": needs_preparation,
            "needs_interview": needs_interview,
            "needs_review": needs_review,
            "phase": "interview" if needs_interview else "general",
            "topic": topic,
        }

    def _extract_topic(self, question: str) -> str:
        """提取问题主题"""
        stop_words = {"的", "了", "吗", "呢", "吧", "是", "在", "有", "和", "与",
                      "what", "is", "how", "to", "the", "a", "an", "do", "does"}
        words = question.split()
        topic_words = [w for w in words if w.lower() not in stop_words]
        return " ".join(topic_words[:5]) if topic_words else question

    def compose_final_answer(self, question: str, results: dict[str, Any]) -> str:
        """汇总所有 Agent 的结果，生成最终回答"""
        sections = []
        sections.append(f"## {question}\n")

        if "preparation" in results:
            sections.append("### 面试前准备\n")
            sections.append(results["preparation"])
            sections.append("")

        if "interview" in results:
            sections.append("### 面试回答指导\n")
            sections.append(results["interview"])
            sections.append("")

        if "review" in results:
            sections.append("### 面试后评审\n")
            sections.append(results["review"])
            sections.append("")

        if "study_plan" in results:
            sections.append("### 学习计划\n")
            sections.append(results["study_plan"])
            sections.append("")

        if "sources" in results and results["sources"]:
            sections.append("### 参考来源\n")
            for source in results["sources"]:
                sections.append(f"- {source}")

        answer = "\n".join(sections)

        if self.llm:
            enhanced = self._enhance_with_llm(question, answer)
            if enhanced:
                return enhanced

        return answer

    def _enhance_with_llm(self, question: str, draft: str) -> str:
        """用 LLM 润色回答"""
        prompt = f"""请将以下面试回答润色，使其更加自然和专业。

原始问题：{question}

草稿：
{draft}

要求：
1. 保持原有的结构和要点
2. 使用更自然的表达
3. 添加适当的过渡句
4. 确保专业术语准确

请直接返回润色后的内容。"""

        return self.call_llm(prompt)
