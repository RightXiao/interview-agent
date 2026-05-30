"""新工作流 - 基于消息传递的多 Agent 协作"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from src.agents.base import MessageBus
from src.agents.coordinator import CoordinatorAgent
from src.agents.interview import InterviewAgent
from src.agents.jd_analyzer import JDAnalyzerAgent
from src.agents.post_interview import PostInterviewAgent
from src.agents.pre_interview import PreInterviewAgent
from src.agents.resume_agent import ResumeAgent
from src.agents.state import AgentResult, AgentState
from src.memory.store import MemoryStore
from src.rag.retriever import format_sources, retrieve_from_store


class InterviewWorkflow:
    """面试工作流 - 协调多个 Agent 完成面试准备"""

    def __init__(
        self,
        base_dir: Path | str = ".",
        llm: Any | None = None,
        top_k: int = 4,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.llm = llm
        self.top_k = top_k

        # 初始化消息总线
        self.message_bus = MessageBus()

        # 初始化 Agent
        self.coordinator = CoordinatorAgent(llm=llm)
        self.pre_interview = PreInterviewAgent(llm=llm)
        self.interview = InterviewAgent(llm=llm)
        self.post_interview = PostInterviewAgent(llm=llm)
        self.jd_analyzer = JDAnalyzerAgent(llm=llm)
        self.resume_agent = ResumeAgent(llm=llm)

        # 注册到消息总线
        for agent in [self.coordinator, self.pre_interview, self.interview,
                      self.post_interview, self.jd_analyzer, self.resume_agent]:
            agent.set_message_bus(self.message_bus)

        # 用户数据（JD 和简历）
        self._jd_text: str = ""
        self._jd_analysis: str = ""
        self._resume_text: str = ""

        # 初始化记忆和 RAG
        self.memory = MemoryStore(self.base_dir / "data" / "memory")
        self.store = None  # 延迟初始化

    def set_store(self, store: Any) -> None:
        """设置向量存储"""
        self.store = store

    def set_jd(self, jd_text: str) -> dict[str, Any]:
        """设置并分析 JD"""
        self._jd_text = jd_text
        result = self.jd_analyzer.execute({"jd_text": jd_text})
        self._jd_analysis = result.get("jd_analysis", "")
        return result

    def set_resume(self, resume_text: str) -> dict[str, Any]:
        """设置并分析简历"""
        self._resume_text = resume_text
        return self.resume_agent.execute({
            "resume_text": resume_text,
            "jd_analysis": self._jd_analysis,
        })

    def analyze_match(self) -> dict[str, Any]:
        """分析简历与 JD 匹配度"""
        if not self._resume_text or not self._jd_analysis:
            return {"match_analysis": "请先设置简历和 JD（使用 /resume 和 /jd 命令）"}
        return {"match_analysis": self.resume_agent.analyze_match(self._resume_text, self._jd_analysis)}

    def run(self, question: str) -> AgentResult:
        """执行工作流"""
        state = AgentState(question=question)

        # 1. 加载上下文
        self._load_context(state)

        # 2. 主 Agent 分析意图
        intent = self.coordinator.analyze_intent(question)
        state.agent_notes["_intent"] = str(intent)

        # 3. 知识检索（如果需要）
        context = ""
        sources = []
        if intent.get("needs_rag") and self.store:
            context, sources = self._retrieve_knowledge(question)
            state.retrieved_context = [{"text": context}]
            state.sources = sources

        # 4. 并行执行子 Agent
        results = self._execute_agents(question, intent, context)

        # 5. 汇总最终回答
        answer = self.coordinator.compose_final_answer(question, results)

        # 6. 保存记忆
        self._save_memory(question, answer)

        return AgentResult(
            answer=answer,
            sources=sources,
            study_plan=results.get("study_plan", ""),
            agent_notes=results,
        )

    def _load_context(self, state: AgentState) -> None:
        """加载上下文"""
        state.profile = self.memory.get_profile()
        state.short_term_memory = self.memory.get_short_term_memory()

    def _retrieve_knowledge(self, question: str) -> tuple[str, list[str]]:
        """检索知识库"""
        if not self.store:
            return "", []

        try:
            results = retrieve_from_store(self.store, question, self.top_k)
            sources = format_sources(results)
            context = "\n".join(item.get("text", "") for item in results)
            return context, sources
        except Exception:
            return "", []

    def _execute_agents(
        self,
        question: str,
        intent: dict[str, Any],
        context: str,
    ) -> dict[str, Any]:
        """并行执行子 Agent"""
        topic = intent.get("topic", question)
        results = {}

        # 准备任务
        tasks = {}
        if intent.get("needs_preparation", True):
            tasks["preparation"] = {"topic": topic, "context": context}

        if intent.get("needs_interview", True):
            tasks["interview"] = {"question": question, "topic": topic, "context": context}

        if intent.get("needs_review", True):
            tasks["review"] = {"question": question, "answer": "", "topic": topic}

        # 并行执行
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}

            if "preparation" in tasks:
                futures["preparation"] = executor.submit(
                    self.pre_interview.execute, tasks["preparation"]
                )

            if "interview" in tasks:
                futures["interview"] = executor.submit(
                    self.interview.execute, tasks["interview"]
                )

            if "review" in tasks:
                futures["review"] = executor.submit(
                    self.post_interview.execute, tasks["review"]
                )

            # 收集结果
            for key, future in futures.items():
                try:
                    result = future.result(timeout=30)
                    results.update(result)
                except Exception as e:
                    results[key] = f"Agent 执行失败: {e}"

        return results

    def _save_memory(self, question: str, answer: str) -> None:
        """保存记忆"""
        self.memory.add_turn("user", question)
        self.memory.add_turn("assistant", answer)

        # 更新用户画像
        updates: dict[str, list[str]] = {}
        lowered = question.lower()
        if "rag" in lowered:
            updates.setdefault("recent_topics", []).append("RAG")
        if "tool" in lowered or "工具" in lowered:
            updates.setdefault("recent_topics", []).append("tool calling")
        if "agent" in lowered or "智能体" in lowered:
            updates.setdefault("recent_topics", []).append("agent")
        if updates:
            self.memory.update_profile(updates)
