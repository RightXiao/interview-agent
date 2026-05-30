"""面试中回答 Agent - 回答生成、追问模拟"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class InterviewAgent(BaseAgent):
    """面试中回答：回答生成、追问模拟、STAR 法则指导"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="interview", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行面试回答任务"""
        question = task.get("question", "")
        topic = task.get("topic", "")
        context = task.get("context", "")
        return {"interview": self.generate_answer(question, topic, context)}

    def generate_answer(self, question: str, topic: str, context: str = "") -> str:
        """生成面试回答指导"""
        if self.llm:
            llm_result = self._llm_generate(question, topic, context)
            if llm_result:
                return llm_result
        return self._template_generate(question, topic, context)

    def _llm_generate(self, question: str, topic: str, context: str) -> str:
        """用 LLM 生成面试回答"""
        prompt = f"""作为面试教练，请为以下面试问题提供回答指导。

问题：{question}
主题：{topic}

{f"参考资料：{context}" if context else ""}

请提供：
1. 回答框架（使用 STAR 法则或总分总结构）
2. 关键要点（3-5 个必须提到的点）
3. 示例回答（简洁版本）
4. 常见追问及应对策略

请用结构化的方式回答。"""
        return self.call_llm(prompt)

    def _template_generate(self, question: str, topic: str, context: str = "") -> str:
        """模板化的面试回答指导"""
        sections = [f"**问题分析：** {question}\n"]

        sections.append("#### 回答框架（STAR 法则）")
        sections.append("- **Situation（情境）：** 描述项目背景和挑战")
        sections.append("- **Task（任务）：** 说明你的具体职责")
        sections.append("- **Action（行动）：** 详细描述你的解决方案")
        sections.append("- **Result（结果）：** 展示成果和收获")

        sections.append("\n#### 关键要点")
        sections.append(f"1. 从 {topic} 的核心原理入手")
        sections.append(f"2. 结合实际项目经验说明")
        sections.append(f"3. 强调解决问题的思路和方法")
        sections.append(f"4. 提及技术选型的考量")
        sections.append(f"5. 总结经验教训和改进方向")

        if context:
            sections.append(f"\n#### 参考知识")
            sections.append(context[:300])

        sections.append("\n#### 常见追问")
        sections.append(f"- 为什么选择 {topic} 而不是其他方案？")
        sections.append(f"- {topic} 的性能瓶颈在哪里？如何优化？")
        sections.append(f"- 如果重新设计，你会如何改进？")

        return "\n".join(sections)
