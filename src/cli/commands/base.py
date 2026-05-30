"""命令基类"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutputType(Enum):
    """输出类型"""
    TEXT = "text"
    MARKDOWN = "markdown"
    TABLE = "table"
    CODE = "code"
    PANEL = "panel"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"
    NONE = "none"


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    message: str = ""
    output: Any = None
    output_type: OutputType = OutputType.TEXT
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandContext:
    """命令执行上下文"""
    workflow: Any = None  # AgentWorkflow
    renderer: Any = None  # OutputRenderer
    session_manager: Any = None  # SessionManager
    # 当前状态
    latest_answer: str = ""
    latest_sources: list[str] = field(default_factory=list)
    latest_study_plan: str = ""
    # 配置
    config: Any = None  # AppConfig


class Command(ABC):
    """命令基类"""

    name: str  # 命令名称（如 "help"）
    aliases: list[str]  # 别名（如 ["h", "?"]）
    description: str  # 短描述
    usage: str  # 用法示例

    @abstractmethod
    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        """执行命令

        Args:
            args: 命令参数
            ctx: 命令上下文

        Returns:
            命令执行结果
        """
        ...

    def completer(self, args: str, ctx: CommandContext) -> list[str]:
        """参数补全

        Args:
            args: 当前输入的参数
            ctx: 命令上下文

        Returns:
            补全建议列表
        """
        return []
