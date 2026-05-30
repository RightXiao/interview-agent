"""命令系统模块"""

from __future__ import annotations

from src.cli.commands.base import Command, CommandContext, CommandResult
from src.cli.commands.builtin import BuiltinCommands
from src.cli.commands.data import DataCommands
from src.cli.commands.document import DocumentCommands
from src.cli.commands.evaluation import EvaluationCommands


class CommandRegistry:
    """命令注册表"""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}
        self._aliases: dict[str, str] = {}  # alias -> command name

    def register(self, command: Command) -> None:
        """注册命令"""
        self._commands[command.name] = command
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def get(self, name: str) -> Command | None:
        """获取命令"""
        # 先尝试直接匹配
        if name in self._commands:
            return self._commands[name]
        # 再尝试别名
        if name in self._aliases:
            return self._commands[self._aliases[name]]
        return None

    def get_all(self) -> dict[str, Command]:
        """获取所有命令"""
        return self._commands.copy()

    def get_command_names(self) -> dict[str, str]:
        """获取命令名称到描述的映射（用于补全）"""
        return {cmd.name: cmd.description for cmd in self._commands.values()}

    def execute(
        self,
        raw: str,
        ctx: CommandContext,
    ) -> CommandResult:
        """解析并执行命令

        Args:
            raw: 原始输入（如 "/import path/to/file.md"）
            ctx: 命令上下文

        Returns:
            命令执行结果
        """
        # 解析命令
        if not raw.startswith("/"):
            return CommandResult(
                success=False,
                message="不是有效的命令",
            )

        # 分离命令名和参数
        parts = raw[1:].split(None, 1)
        cmd_name = parts[0] if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        # 获取命令
        cmd = self.get(cmd_name)
        if cmd is None:
            return CommandResult(
                success=False,
                message=f"未知命令: /{cmd_name}",
            )

        # 执行命令
        return cmd.execute(args, ctx)


def create_default_registry() -> CommandRegistry:
    """创建默认的命令注册表

    Returns:
        包含所有内置命令的 CommandRegistry
    """
    registry = CommandRegistry()

    # 注册内置命令
    for cmd in BuiltinCommands.all():
        registry.register(cmd)

    # 注册数据命令
    for cmd in DataCommands.all():
        registry.register(cmd)

    # 注册文档命令
    for cmd in DocumentCommands.all():
        registry.register(cmd)

    # 注册评估命令
    for cmd in EvaluationCommands.all():
        registry.register(cmd)

    return registry
