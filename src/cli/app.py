"""主应用入口 - Claude Code 风格的 CLI"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.agents.graph import AgentWorkflow
from src.cli.commands import CommandRegistry, create_default_registry
from src.cli.commands.base import CommandContext, OutputType
from src.cli.session import SessionManager
from src.cli.ui.input_box import InputBox
from src.cli.ui.output import OutputRenderer
from src.cli.ui.spinner import Spinner
from src.cli.ui.theme import DEFAULT_THEME
from src.config import AppConfig
from src.llm.client import OpenAICompatibleClient
from src.rag.indexer import VectorStore


def _is_tty() -> bool:
    return sys.stdin.isatty()


class InterviewApp:
    """Claude Code 风格的面试助手 CLI"""

    def __init__(self, base_dir: Path | str = ".", config: AppConfig | None = None) -> None:
        self.base_dir = Path(base_dir)
        self.config = config or AppConfig.from_env(self.base_dir)
        self.theme = DEFAULT_THEME

        # 初始化 UI 组件
        self.renderer = OutputRenderer(self.theme)
        self.console = self.renderer.console

        # 初始化会话管理
        self.session_manager = SessionManager(self.base_dir / "data" / "sessions")
        self._current_session_id: str | None = None

        # 初始化命令系统
        self.commands = create_default_registry()

        # 初始化输入框
        history_file = str(self.base_dir / "data" / ".cli_history")
        self.input_box = InputBox(
            history_file=history_file,
            commands=self.commands.get_command_names(),
            theme=self.theme,
        )

        # 初始化工作流
        self._init_workflow()

        # 当前状态
        self.latest_answer = ""
        self.latest_sources: list[str] = []
        self.latest_study_plan = ""

    def _init_workflow(self) -> None:
        """初始化 Agent 工作流"""
        self.store = VectorStore(
            persist_dir=self.base_dir / "data" / "vector_store",
            embedding_model=self.config.embedding_model,
            base_url=self.config.llm_base_url,
            api_key=self.config.llm_api_key,
        )
        llm = OpenAICompatibleClient(config=self.config) if self.config.validate_llm() == [] else None
        self.workflow = AgentWorkflow(
            base_dir=self.base_dir,
            llm=llm,
            top_k=self.config.rag_top_k,
            config=self.config,
            store=self.store,
        )

    def _show_banner(self) -> None:
        """显示启动横幅"""
        title = Text("Interview Coach", style=f"bold {self.theme.primary}")
        subtitle = Text("AI 智能体面试准备工具", style=self.theme.text_dim)

        content = Text()
        content.append_text(title)
        content.append("\n")
        content.append_text(subtitle)

        panel = Panel(
            content,
            border_style=self.theme.border,
            padding=(1, 2),
            subtitle="[text.muted]输入 / 查看命令[/text.muted]",
        )
        self.console.print(panel)
        self.console.print()

    def _create_command_context(self) -> CommandContext:
        """创建命令上下文"""
        ctx = CommandContext(
            workflow=self.workflow,
            renderer=self.renderer,
            session_manager=self.session_manager,
            latest_answer=self.latest_answer,
            latest_sources=self.latest_sources,
            latest_study_plan=self.latest_study_plan,
            config=self.config,
        )
        # 传递命令注册表供 help 命令使用
        ctx._command_registry = self.commands
        return ctx

    def _process_question(self, question: str) -> None:
        """处理用户提问"""
        # 创建会话（如果需要）
        if not self._current_session_id:
            self._current_session_id = self.session_manager.create_session()

        # 添加用户消息到会话
        self.session_manager.add_turn(self._current_session_id, "user", question)

        # 显示 spinner 并处理
        with Spinner("思考中...", console=self.console):
            try:
                result = self.workflow.run(question)
            except Exception as e:
                self.renderer.print_error(f"处理失败: {e}")
                return

        # 更新状态
        self.latest_answer = result.answer
        self.latest_sources = result.sources
        self.latest_study_plan = result.study_plan

        # 渲染回答
        self.console.print()
        self.renderer.print_markdown(result.answer)

        # 显示来源
        if result.sources:
            self.console.print()
            self.console.print("[text.dim]来源:[/text.dim]")
            for source in result.sources:
                self.console.print(f"  [text.muted]• {source}[/text.muted]")

        self.console.print()

        # 添加助手回复到会话
        self.session_manager.add_turn(self._current_session_id, "assistant", result.answer)

    def _execute_command(self, raw: str) -> bool:
        """执行命令

        Returns:
            True 如果应该退出程序
        """
        ctx = self._create_command_context()
        result = self.commands.execute(raw, ctx)

        # 检查是否需要退出
        if result.data.get("action") == "exit":
            return True

        # 渲染结果
        if result.output_type == OutputType.NONE:
            pass  # 不输出
        elif result.output_type == OutputType.MARKDOWN:
            self.renderer.print_markdown(result.message)
        elif result.output_type == OutputType.ERROR:
            self.renderer.print_error(result.message)
        elif result.output_type == OutputType.SUCCESS:
            self.renderer.print_success(result.message)
        elif result.output_type == OutputType.WARNING:
            self.renderer.print_warning(result.message)
        elif result.output_type == OutputType.INFO:
            self.renderer.print_info(result.message)
        else:
            if result.message:
                self.console.print(result.message)

        # 处理特殊动作
        action = result.data.get("action")
        if action == "resume":
            session_data = result.data.get("session")
            if session_data:
                self._restore_session(session_data)

        return False

    def _restore_session(self, session_data: dict) -> None:
        """恢复会话状态"""
        self._current_session_id = session_data.get("id")
        turns = session_data.get("turns", [])

        # 恢复工作流记忆
        if hasattr(self.workflow, 'memory'):
            self.workflow.memory.clear_short_term_memory()
            for turn in turns:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if role in ("user", "assistant"):
                    self.workflow.memory.add_turn(role, content)

        self.console.print(f"[text.dim]已恢复 {len(turns)} 轮对话[/text.dim]")

    def run(self) -> None:
        """主循环"""
        self._show_banner()
        use_tty = _is_tty()

        while True:
            try:
                # 获取用户输入
                if use_tty:
                    user_input = self.input_box.prompt()
                else:
                    user_input = input("> ")

                # 跳过空输入
                if not user_input.strip():
                    continue

                # 执行命令或处理问题
                if user_input.startswith("/"):
                    should_exit = self._execute_command(user_input)
                    if should_exit:
                        break
                else:
                    self._process_question(user_input)

            except KeyboardInterrupt:
                # Ctrl+C
                if use_tty:
                    self.console.print("\n[text.dim]使用 /exit 退出[/text.dim]")
                else:
                    self.console.print("\nBye.")
                break

            except EOFError:
                # Ctrl+D
                break

            except Exception as e:
                self.renderer.print_error(f"发生错误: {e}")
                continue

        # 退出时保存会话
        self._save_on_exit()
        if use_tty:
            self.console.print("\n[primary]再见！[/primary]\n")

    def _save_on_exit(self) -> None:
        """退出时保存会话快照"""
        if self._current_session_id and hasattr(self.workflow, 'memory'):
            turns = self.workflow.memory.get_short_term_memory()
            if turns:
                self.workflow.memory.save_session_snapshot("auto")


def run() -> None:
    """CLI 入口点"""
    app = InterviewApp()
    app.run()


if __name__ == "__main__":
    run()
