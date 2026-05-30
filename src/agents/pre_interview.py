"""面试前准备 Agent - 知识检索、背景准备"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class PreInterviewAgent(BaseAgent):
    """面试前准备：知识检索、背景准备、常见问题收集"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="pre_interview", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行面试前准备任务"""
        topic = task.get("topic", "")
        context = task.get("context", "")
        return {"preparation": self.prepare(topic, context)}

    def prepare(self, topic: str, context: str = "") -> str:
        """准备面试背景知识"""
        if self.llm:
            llm_result = self._llm_prepare(topic, context)
            if llm_result:
                return llm_result
        return self._template_prepare(topic, context)

    def _llm_prepare(self, topic: str, context: str) -> str:
        """用 LLM 生成面试前准备内容"""
        prompt = f"""作为面试准备顾问，请为以下技术主题准备面试背景知识。

主题：{topic}

{f"参考资料：{context}" if context else ""}

请提供：
1. 核心概念解释（2-3 句话）
2. 关键技术要点（3-5 个）
3. 常见面试考点
4. 需要准备的项目经验示例

请用简洁的要点形式回答。"""
        return self.call_llm(prompt)

    def _template_prepare(self, topic: str, context: str = "") -> str:
        """模板化的面试前准备"""
        sections = [f"**{topic}** 面试准备要点：\n"]

        sections.append("#### 核心概念")
        if context:
            sections.append(f"基于检索到的知识：{context[:200]}...")
        else:
            sections.append(f"- 理解 {topic} 的基本原理和应用场景")
            sections.append(f"- 掌握 {topic} 的核心组件和工作流程")
            sections.append(f"- 了解 {topic} 的优缺点和适用场景")

        sections.append("\n#### 关键技术要点")
        sections.append(f"1. {topic} 的架构设计")
        sections.append(f"2. {topic} 的核心算法/流程")
        sections.append(f"3. {topic} 的性能优化")
        sections.append(f"4. {topic} 的常见问题和解决方案")

        sections.append("\n#### 面试常见考点")
        sections.append(f"- {topic} 的工作原理是什么？")
        sections.append(f"- {topic} 有哪些优缺点？")
        sections.append(f"- 如何在项目中应用 {topic}？")

        sections.append("\n#### 项目经验准备")
        sections.append(f"- 准备一个使用 {topic} 的项目案例")
        sections.append(f"- 描述在项目中遇到的挑战和解决方案")

        return "\n".join(sections)
