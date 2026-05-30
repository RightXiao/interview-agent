"""面试后总结 Agent - 评审回答、学习计划"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class PostInterviewAgent(BaseAgent):
    """面试后总结：回答评审、学习计划、改进建议"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="post_interview", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行面试后总结任务"""
        question = task.get("question", "")
        answer = task.get("answer", "")
        topic = task.get("topic", "")
        return {
            "review": self.review_answer(question, answer, topic),
            "study_plan": self.generate_study_plan(topic),
        }

    def review_answer(self, question: str, answer: str, topic: str) -> str:
        """评审面试回答"""
        if self.llm:
            llm_result = self._llm_review(question, answer, topic)
            if llm_result:
                return llm_result
        return self._template_review(question, answer, topic)

    def _llm_review(self, question: str, answer: str, topic: str) -> str:
        """用 LLM 评审回答"""
        prompt = f"""作为面试评审专家，请评审以下面试回答。

问题：{question}
主题：{topic}
回答：{answer[:500] if answer else "（无回答）"}

请从以下维度评审：
1. 内容完整性（是否覆盖关键点）
2. 逻辑清晰度（结构是否合理）
3. 技术深度（是否展示专业能力）
4. 表达质量（是否简洁明了）

给出评分（1-10）和具体改进建议。"""
        return self.call_llm(prompt)

    def _template_review(self, question: str, answer: str, topic: str) -> str:
        """模板化的回答评审"""
        sections = ["#### 回答评审\n"]

        sections.append("| 维度 | 评价 | 改进建议 |")
        sections.append("|------|------|----------|")
        sections.append(f"| 内容完整性 | ⭐⭐⭐ | 确保覆盖 {topic} 的核心要点 |")
        sections.append("| 逻辑清晰度 | ⭐⭐⭐⭐ | 使用 STAR 法则组织回答 |")
        sections.append("| 技术深度 | ⭐⭐⭐ | 添加具体的技术细节和数据 |")
        sections.append("| 表达质量 | ⭐⭐⭐⭐ | 保持简洁，避免冗长 |")

        sections.append("\n#### 改进建议")
        sections.append(f"1. 补充 {topic} 的核心原理说明")
        sections.append("2. 添加具体的性能数据或指标")
        sections.append("3. 说明技术选型的权衡考量")

        return "\n".join(sections)

    def generate_study_plan(self, topic: str) -> str:
        """生成学习计划"""
        if self.llm:
            llm_result = self._llm_study_plan(topic)
            if llm_result:
                return llm_result
        return self._template_study_plan(topic)

    def _llm_study_plan(self, topic: str) -> str:
        """用 LLM 生成学习计划"""
        prompt = f"""作为学习规划师，请为以下技术主题制定学习计划。

主题：{topic}

请制定一个 2-4 周的学习计划，包括：
1. 每周学习目标
2. 推荐学习资源
3. 实践项目建议
4. 自测方法

请用结构化的格式回答。"""
        return self.call_llm(prompt)

    def _template_study_plan(self, topic: str) -> str:
        """模板化的学习计划"""
        sections = [f"#### {topic} 学习计划\n"]

        sections.append("**第 1 周：基础概念**")
        sections.append(f"- 学习 {topic} 的核心原理")
        sections.append(f"- 阅读官方文档和入门教程")

        sections.append("\n**第 2 周：深入理解**")
        sections.append(f"- 研究 {topic} 的架构设计")
        sections.append(f"- 学习最佳实践和设计模式")

        sections.append("\n**第 3 周：实战应用**")
        sections.append(f"- 在项目中应用 {topic}")
        sections.append(f"- 解决实际问题和挑战")

        sections.append("\n**第 4 周：总结提升**")
        sections.append(f"- 总结 {topic} 的使用经验")
        sections.append(f"- 准备面试问答")

        return "\n".join(sections)
