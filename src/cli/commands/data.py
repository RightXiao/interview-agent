"""数据命令 - sessions, resume 等"""

from __future__ import annotations

from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


class SessionsCommand(Command):
    """查看会话列表"""

    name = "sessions"
    aliases = ["ls"]
    description = "查看历史会话列表"
    usage = "/sessions"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not ctx.session_manager:
            return CommandResult(
                success=False,
                message="会话管理器未初始化",
                output_type=OutputType.ERROR,
            )

        sessions = ctx.session_manager.list_sessions()
        if not sessions:
            return CommandResult(
                success=True,
                message="没有历史会话",
                output_type=OutputType.TEXT,
            )

        lines = ["# 历史会话\n"]
        for session in sessions:
            lines.append(f"- **{session.id}** - {session.created_at}")
            if session.preview:
                lines.append(f"  {session.preview[:50]}...")

        return CommandResult(
            success=True,
            message="\n".join(lines),
            output_type=OutputType.MARKDOWN,
        )


class ResumeCommand(Command):
    """恢复会话"""

    name = "resume"
    aliases = ["r"]
    description = "恢复之前的会话"
    usage = "/resume <会话ID>"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message="请指定会话ID\n\n用法: /resume <会话ID>\n\n使用 `/sessions` 查看可用会话",
                output_type=OutputType.ERROR,
            )

        if not ctx.session_manager:
            return CommandResult(
                success=False,
                message="会话管理器未初始化",
                output_type=OutputType.ERROR,
            )

        session = ctx.session_manager.load_session(args)
        if not session:
            return CommandResult(
                success=False,
                message=f"会话不存在: {args}",
                output_type=OutputType.ERROR,
            )

        return CommandResult(
            success=True,
            message=f"已恢复会话: **{args}**",
            output_type=OutputType.MARKDOWN,
            data={"action": "resume", "session": session},
        )


class DataCommands:
    """数据命令集合"""

    @staticmethod
    def all() -> list[Command]:
        """返回所有数据命令"""
        return [
            SessionsCommand(),
            ResumeCommand(),
        ]
