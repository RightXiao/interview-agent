"""加载动画组件 - Claude Code 风格的 Spinner"""

from __future__ import annotations

import time
from threading import Event, Thread

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class Spinner:
    """Claude Code 风格的加载动画"""

    # Braille 字符动画帧
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(
        self,
        message: str = "思考中...",
        console: Console | None = None,
    ) -> None:
        self.message = message
        self._console = console or Console()
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._live: Live | None = None
        self._start_time: float = 0

    def _render(self) -> Panel:
        """渲染当前帧"""
        frame_idx = int(time.time() * 10) % len(self.FRAMES)
        frame = self.FRAMES[frame_idx]

        # 计算已用时间
        elapsed = time.time() - self._start_time
        if elapsed < 1:
            time_str = ""
        elif elapsed < 60:
            time_str = f"  {elapsed:.1f}s"
        else:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            time_str = f"  {minutes}m{seconds}s"

        text = Text()
        text.append(f"  {frame} ", style="primary")
        text.append(self.message, style="text")
        text.append(time_str, style="text.dim")

        return Panel(text, style="border", padding=(0, 1))

    def _animate(self) -> None:
        """动画线程"""
        while not self._stop_event.is_set():
            if self._live:
                self._live.update(self._render())
            time.sleep(0.1)  # 10fps

    def start(self) -> None:
        """启动动画"""
        self._start_time = time.time()
        self._stop_event.clear()
        self._live = Live(
            self._render(),
            console=self._console,
            refresh_per_second=10,
            transient=True,
        )
        self._live.start()
        self._thread = Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止动画"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=0.5)
        if self._live:
            self._live.stop()
            self._live = None

    def update(self, message: str) -> None:
        """更新消息"""
        self.message = message

    def __enter__(self) -> Spinner:
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()


class AgentSpinner:
    """Agent 专用的 Spinner，支持多步骤显示"""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()
        self._current_spinner: Spinner | None = None

    def step(self, agent: str, message: str) -> Spinner:
        """开始一个新的 Agent 步骤"""
        # 停止上一个 spinner
        if self._current_spinner:
            self._current_spinner.stop()

        # 创建新的 spinner
        self._current_spinner = Spinner(
            message=f"[agent.{agent.lower()}]{agent}[/] {message}",
            console=self._console,
        )
        self._current_spinner.start()
        return self._current_spinner

    def stop(self) -> None:
        """停止当前 spinner"""
        if self._current_spinner:
            self._current_spinner.stop()
            self._current_spinner = None

    def __enter__(self) -> AgentSpinner:
        return self

    def __exit__(self, *args) -> None:
        self.stop()
