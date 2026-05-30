"""输出渲染器 - 封装 rich Console"""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme as RichTheme

from src.cli.ui.theme import DEFAULT_THEME, Theme


class OutputRenderer:
    """Claude Code 风格的输出渲染器"""

    def __init__(self, theme: Theme | None = None) -> None:
        self.theme = theme or DEFAULT_THEME
        self._console = Console(
            theme=self._build_rich_theme(),
            highlight=True,
            soft_wrap=True,
        )

    def _build_rich_theme(self) -> RichTheme:
        """构建 rich 主题"""
        return RichTheme(
            {
                "primary": self.theme.primary,
                "secondary": self.theme.secondary,
                "accent": self.theme.accent,
                "text": self.theme.text,
                "text.dim": self.theme.text_dim,
                "text.muted": self.theme.text_muted,
                "success": self.theme.success,
                "warning": self.theme.warning,
                "error": self.theme.error,
                "info": self.theme.info,
                "border": self.theme.border,
                "command": self.theme.command,
                "command.desc": self.theme.command_desc,
                "agent.coordinator": self.theme.agent_coordinator,
                "agent.explainer": self.theme.agent_explainer,
                "agent.interviewer": self.theme.agent_interviewer,
                "agent.reviewer": self.theme.agent_reviewer,
                "agent.planner": self.theme.agent_planner,
            }
        )

    @property
    def console(self) -> Console:
        """获取底层 Console 实例"""
        return self._console

    def print(self, *args, **kwargs) -> None:
        """打印内容"""
        self._console.print(*args, **kwargs)

    def print_markdown(self, content: str) -> None:
        """渲染 Markdown 内容"""
        md = Markdown(content)
        self._console.print(md)

    def print_panel(
        self,
        content: str,
        title: str = "",
        style: str = "border",
        padding: tuple[int, int] = (1, 2),
    ) -> None:
        """渲染 Panel"""
        panel = Panel(
            content,
            title=title,
            style=style,
            padding=padding,
        )
        self._console.print(panel)

    def print_code(self, code: str, language: str = "python") -> None:
        """渲染代码块"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self._console.print(syntax)

    def print_table(
        self,
        title: str,
        columns: list[str],
        rows: list[list[str]],
        style: str = "border",
    ) -> None:
        """渲染表格"""
        table = Table(title=title, style=style)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self._console.print(table)

    def print_error(self, message: str) -> None:
        """打印错误信息"""
        self._console.print(f"[error]✗ {message}[/error]")

    def print_success(self, message: str) -> None:
        """打印成功信息"""
        self._console.print(f"[success]✓ {message}[/success]")

    def print_warning(self, message: str) -> None:
        """打印警告信息"""
        self._console.print(f"[warning]⚠ {message}[/warning]")

    def print_info(self, message: str) -> None:
        """打印信息"""
        self._console.print(f"[info]ℹ {message}[/info]")

    def print_agent_step(self, agent: str, message: str) -> None:
        """打印 Agent 处理步骤"""
        style = f"agent.{agent.lower()}"
        self._console.print(f"[{style}]⟐ {agent}:[/{style}] {message}")

    def print_command_help(self, name: str, description: str, usage: str = "") -> None:
        """打印命令帮助信息"""
        self._console.print(f"  [command]{name}[/command]")
        self._console.print(f"    [command.desc]{description}[/command.desc]")
        if usage:
            self._console.print(f"    [text.muted]{usage}[/text.muted]")

    def clear(self) -> None:
        """清屏"""
        self._console.clear()

    def print_divider(self, char: str = "─", style: str = "border") -> None:
        """打印分隔线"""
        width = self._console.width
        self._console.print(f"[{style}]{char * width}[/{style}]")
