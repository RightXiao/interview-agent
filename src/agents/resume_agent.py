"""简历项目深度挖掘 Agent"""

from __future__ import annotations

from typing import Any

from src.agents.base import BaseAgent


class ResumeAgent(BaseAgent):
    """简历项目深度挖掘，分析与 JD 匹配度"""

    def __init__(self, llm: Any | None = None) -> None:
        super().__init__(name="resume", llm=llm)

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """执行简历分析任务"""
        resume_text = task.get("resume_text", "")
        jd_analysis = task.get("jd_analysis", "")

        if not resume_text:
            return {"resume_analysis": "请提供简历文本"}

        result = {
            "resume_analysis": self.analyze_resume(resume_text),
            "project_deep_dive": self.deep_dive_projects(resume_text),
        }

        if jd_analysis:
            result["match_analysis"] = self.analyze_match(resume_text, jd_analysis)

        return result

    def analyze_resume(self, resume_text: str) -> str:
        """分析简历"""
        if self.llm:
            result = self._llm_analyze(resume_text)
            if result:
                return result
        return self._template_analyze(resume_text)

    def _llm_analyze(self, resume_text: str) -> str:
        """用 LLM 分析简历"""
        prompt = f"""作为职业顾问，请分析以下简历。

简历内容：
{resume_text[:2000]}

请提取并分析：
1. 核心技能清单
2. 项目经历（项目名称、技术栈、职责、成果）
3. 工作经验亮点
4. 教育背景
5. 简历亮点
6. 改进建议

请用结构化的 Markdown 格式回答。"""
        return self.call_llm(prompt)

    def _template_analyze(self, resume_text: str) -> str:
        """模板化分析"""
        sections = ["#### 简历分析\n"]

        skills = self._extract_skills(resume_text)
        sections.append("**核心技能：**")
        if skills:
            sections.append(", ".join(skills))
        else:
            sections.append("- 未识别到明确技能关键词")

        sections.append("\n**项目经历准备：**")
        sections.append("- 准备 2-3 个核心项目的 STAR 法则回答")
        sections.append("- 量化项目成果（性能提升、用户增长等）")
        sections.append("- 准备项目中的技术难点和解决方案")

        sections.append("\n**简历改进建议：**")
        sections.append("1. 突出量化成果")
        sections.append("2. 强调与目标岗位相关的经验")
        sections.append("3. 使用动词开头描述职责")

        return "\n".join(sections)

    def _extract_skills(self, text: str) -> list[str]:
        """提取技能关键词"""
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

    def analyze_match(self, resume_text: str, jd_analysis: str) -> str:
        """分析简历与 JD 的匹配度"""
        if self.llm:
            prompt = f"""作为职业顾问，请分析简历与岗位 JD 的匹配度。

简历内容：
{resume_text[:1500]}

JD 分析：
{jd_analysis[:1000]}

请分析：
1. 技能匹配度（匹配的技能、缺失的技能）
2. 经验匹配度
3. 整体匹配评分（1-10）
4. 提升匹配度的建议

请用结构化的 Markdown 格式回答。"""
            result = self.call_llm(prompt)
            if result:
                return result

        return self._template_match(resume_text, jd_analysis)

    def _template_match(self, resume_text: str, jd_analysis: str) -> str:
        """模板化匹配分析"""
        sections = ["#### 简历与 JD 匹配度分析\n"]

        resume_skills = set(self._extract_skills(resume_text))
        jd_skills = set()
        for line in jd_analysis.split("\n"):
            for word in ["Python", "Java", "React", "Docker", "MySQL", "Redis"]:
                if word.lower() in line.lower():
                    jd_skills.add(word)

        matched = resume_skills & jd_skills
        missing = jd_skills - resume_skills

        sections.append("**匹配的技能：**")
        sections.append(", ".join(matched) if matched else "- 未找到明确匹配")

        sections.append("\n**缺失的技能：**")
        sections.append(", ".join(missing) if missing else "- 无明显缺失")

        sections.append("\n**提升建议：**")
        sections.append("1. 在简历中突出匹配的技能经验")
        sections.append("2. 准备缺失技能的学习计划")

        return "\n".join(sections)

    def deep_dive_projects(self, resume_text: str) -> str:
        """深度挖掘项目"""
        if self.llm:
            prompt = f"""作为面试教练，请深度挖掘以下简历中的项目经历。

简历内容：
{resume_text[:2000]}

请为每个主要项目准备：
1. 项目背景和目标（1-2 句）
2. 技术架构（用了什么技术栈）
3. 你的具体职责
4. 技术难点和解决方案
5. 量化成果
6. 可能的面试追问及回答

请用 STAR 法则组织回答。"""
            result = self.call_llm(prompt)
            if result:
                return result

        return self._template_deep_dive()

    def _template_deep_dive(self) -> str:
        """模板化项目深度挖掘"""
        sections = ["#### 项目深度挖掘\n"]

        sections.append("**准备框架（STAR 法则）：**\n")
        sections.append("| 项目 | 情境(S) | 任务(T) | 行动(A) | 结果(R) |")
        sections.append("|------|---------|---------|---------|---------|")
        sections.append("| 项目1 | 业务背景 | 你的职责 | 技术方案 | 量化成果 |")

        sections.append("\n**常见追问准备：**")
        sections.append("1. 项目中遇到的最大技术挑战是什么？")
        sections.append("2. 为什么选择这个技术方案？")
        sections.append("3. 如果重新设计，会如何改进？")

        return "\n".join(sections)
