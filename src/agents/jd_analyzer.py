"""岗位 JD 分析 Agent"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class JDAnalyzerAgent(BaseAgent):
    """分析岗位 JD，提取关键要求"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="jd_analyzer", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行 JD 分析任务"""
        jd_text = task.get("jd_text", "")
        if not jd_text:
            return {"jd_analysis": "请提供岗位 JD 文本"}
        return {"jd_analysis": self.analyze_jd(jd_text)}

    def analyze_jd(self, jd_text: str) -> str:
        """分析 JD"""
        if self.llm:
            result = self._llm_analyze(jd_text)
            if result:
                return result
        return self._template_analyze(jd_text)

    def _llm_analyze(self, jd_text: str) -> str:
        """用 LLM 分析 JD"""
        prompt = f"""作为招聘专家，请分析以下岗位 JD。

JD 内容：
{jd_text[:2000]}

请提取并分析：
1. 岗位名称和级别
2. 技术栈要求（列出所有技术关键词）
3. 软技能要求
4. 经验年限要求
5. 核心职责（3-5 条）
6. 加分项
7. 面试重点预测

请用结构化的 Markdown 格式回答。"""
        return self.call_llm(prompt)

    def _template_analyze(self, jd_text: str) -> str:
        """模板化分析"""
        sections = ["#### 岗位 JD 分析\n"]

        tech_keywords = self._extract_tech_keywords(jd_text)
        sections.append("**技术栈要求：**")
        if tech_keywords:
            sections.append(", ".join(tech_keywords))
        else:
            sections.append("- 未识别到明确技术关键词")

        soft_skills = self._extract_soft_skills(jd_text)
        sections.append("\n**软技能要求：**")
        if soft_skills:
            for skill in soft_skills:
                sections.append(f"- {skill}")
        else:
            sections.append("- 未识别到明确软技能要求")

        sections.append("\n**面试准备建议：**")
        sections.append("1. 准备技术栈相关的项目经验")
        sections.append("2. 准备软技能的 STAR 法则回答")
        sections.append("3. 研究公司背景和业务")

        return "\n".join(sections)

    def _extract_tech_keywords(self, text: str) -> list[str]:
        """提取技术关键词"""
        tech_words = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "FastAPI",
            "Spring", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git",
            "机器学习", "深度学习", "NLP", "计算机视觉", "大模型", "LLM",
            "RAG", "向量数据库", "微服务", "分布式", "高并发", "大数据",
        ]
        found = []
        text_lower = text.lower()
        for word in tech_words:
            if word.lower() in text_lower:
                found.append(word)
        return found

    def _extract_soft_skills(self, text: str) -> list[str]:
        """提取软技能"""
        skill_patterns = {
            "沟通能力": ["沟通", "表达", "交流"],
            "团队协作": ["团队", "协作", "合作"],
            "领导力": ["领导", "管理", "带队"],
            "解决问题": ["问题解决", "解决问题", "分析能力"],
            "学习能力": ["学习", "自驱", "成长"],
            "抗压能力": ["抗压", "压力", "高强度"],
        }
        found = []
        for skill, keywords in skill_patterns.items():
            if any(kw in text for kw in keywords):
                found.append(skill)
        return found
