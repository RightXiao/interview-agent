"""底部输入框组件 - 使用 prompt_toolkit 实现"""

from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from src.cli.ui.theme import DEFAULT_THEME, Theme


class CommandCompleter(Completer):
    """命令补全器"""

    def __init__(self, commands: dict[str, str]) -> None:
        """
        Args:
            commands: 命令名称到描述的映射
        """
        self.commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # 只在输入以 / 开头时补全
        if not text.startswith("/"):
            return

        # 获取当前输入的命令部分
        word = text[1:]  # 去掉 /

        for name, desc in self.commands.items():
            cmd = name.lstrip("/")
            if cmd.startswith(word):
                yield Completion(
                    cmd,
                    start_position=-len(word),
                    display_meta=desc,
                )


class InputBox:
    """Claude Code 风格的底部输入框"""

    def __init__(
        self,
        history_file: str | None = None,
        commands: dict[str, str] | None = None,
        theme: Theme | None = None,
    ) -> None:
        self.theme = theme or DEFAULT_THEME
        self._commands = commands or {}

        # 创建历史记录
        history = FileHistory(history_file) if history_file else None

        # 创建补全器
        completer = CommandCompleter(self._commands) if self._commands else None

        # 创建快捷键绑定
        self._bindings = self._create_keybindings()

        # 创建样式
        self._style = self._create_style()

        # 创建 PromptSession
        self._session: PromptSession[str] = PromptSession(
            history=history,
            completer=completer,
            key_bindings=self._bindings,
            style=self._style,
            multiline=False,  # 单行模式，通过快捷键切换
            wrap_lines=True,
        )

    def _create_style(self) -> Style:
        """创建 prompt_toolkit 样式"""
        return Style.from_dict(
            {
                "prompt": f"bold {self.theme.primary}",
                "input": self.theme.text,
                "completion-menu": "bg:#2A2A2A",
                "completion-menu.completion": f"fg:{self.theme.text}",
                "completion-menu.completion.current": f"bg:{self.theme.selected} fg:{self.theme.text}",
                "completion-menu.meta.completion": f"fg:{self.theme.text_dim}",
                "completion-menu.meta.completion.current": f"fg:{self.theme.text}",
                "auto-suggestion": f"fg:{self.theme.text_muted}",
            }
        )

    def _create_keybindings(self) -> KeyBindings:
        """创建快捷键绑定"""
        bindings = KeyBindings()

        @bindings.add("c-c")
        def _(event):
            """Ctrl+C: 中断"""
            event.app.exit(exception=KeyboardInterrupt)

        @bindings.add("c-d")
        def _(event):
            """Ctrl+D: 退出（仅在空输入时）"""
            if not event.app.current_buffer.text:
                event.app.exit(exception=EOFError)

        @bindings.add("escape", "enter")
        @bindings.add("c-j")
        def _(event):
            """Alt+Enter 或 Ctrl+J: 插入换行"""
            event.app.current_buffer.insert_text("\n")

        return bindings

    def prompt(self, prompt_text: str = "❯ ") -> str:
        """获取用户输入

        Args:
            prompt_text: 提示符文本

        Returns:
            用户输入的文本

        Raises:
            KeyboardInterrupt: 用户按 Ctrl+C
            EOFError: 用户按 Ctrl+D
        """
        try:
            return self._session.prompt(prompt_text)
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise

    @property
    def commands(self) -> dict[str, str]:
        """获取命令列表"""
        return self._commands

    @commands.setter
    def commands(self, value: dict[str, str]) -> None:
        """更新命令列表"""
        self._commands = value
        # 更新补全器
        self._session.completer = CommandCompleter(value) if value else None
