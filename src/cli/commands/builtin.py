"""内置命令 - help, clear, exit, model, config 等"""

from __future__ import annotations

from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


class HelpCommand(Command):
    """显示帮助信息"""

    name = "help"
    aliases = ["h", "?"]
    description = "显示所有可用命令"
    usage = "/help [命令名]"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        # 通过 app 获取命令注册表（通过 ctx 传递）
        registry = getattr(ctx, '_command_registry', None)
        if not registry:
            # 回退：从 workflow 的 app 引用获取
            app = getattr(ctx.workflow, '_app', None)
            if app:
                registry = getattr(app, 'commands', None)

        if not registry:
            return CommandResult(
                success=True,
                message="命令系统未初始化",
                output_type=OutputType.TEXT,
            )

        if args:
            return self._show_command_help(args, registry)

        # 显示所有命令
        commands = registry.get_all()
        if not commands:
            return CommandResult(
                success=True,
                message="没有可用的命令",
                output_type=OutputType.TEXT,
            )

        # 构建输出
        lines = ["# 可用命令\n"]

        # 按分类组织
        categories: dict[str, list[Command]] = {
            "内置命令": [],
            "数据命令": [],
            "文档命令": [],
            "评估命令": [],
        }

        for cmd in commands.values():
            category = getattr(cmd, 'category', '内置命令')
            categories.get(category, categories["内置命令"]).append(cmd)

        for category, cmds in categories.items():
            if cmds:
                lines.append(f"## {category}\n")
                for cmd in cmds:
                    lines.append(f"- **/{cmd.name}** - {cmd.description}")
                    if cmd.usage:
                        lines.append(f"  用法: `{cmd.usage}`")
                lines.append("")

        return CommandResult(
            success=True,
            message="\n".join(lines),
            output_type=OutputType.MARKDOWN,
        )

    def _show_command_help(self, cmd_name: str, registry) -> CommandResult:
        """显示特定命令的帮助"""
        cmd = registry.get(cmd_name)
        if not cmd:
            return CommandResult(
                success=False,
                message=f"未知命令: /{cmd_name}",
                output_type=OutputType.ERROR,
            )

        lines = [
            f"# /{cmd.name}",
            f"\n{cmd.description}\n",
        ]
        if cmd.usage:
            lines.append(f"**用法:** `{cmd.usage}`")
        if cmd.aliases:
            lines.append(f"**别名:** {', '.join(f'/{a}' for a in cmd.aliases)}")

        return CommandResult(
            success=True,
            message="\n".join(lines),
            output_type=OutputType.MARKDOWN,
        )


class ClearCommand(Command):
    """清屏"""

    name = "clear"
    aliases = ["cls"]
    description = "清空屏幕"
    usage = "/clear"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if ctx.renderer:
            ctx.renderer.clear()
        return CommandResult(
            success=True,
            message="",
            output_type=OutputType.NONE,
        )


class ExitCommand(Command):
    """退出程序"""

    name = "exit"
    aliases = ["quit", "q"]
    description = "退出程序"
    usage = "/exit"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        return CommandResult(
            success=True,
            message="exit",
            output_type=OutputType.NONE,
            data={"action": "exit"},
        )


class ModelCommand(Command):
    """切换模型"""

    name = "model"
    aliases = ["m"]
    description = "查看或切换当前模型"
    usage = "/model [模型名称]"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            # 显示当前模型
            current = getattr(ctx.config, 'llm_model', '未配置') if ctx.config else '未配置'
            return CommandResult(
                success=True,
                message=f"当前模型: **{current}**\n\n使用 `/model <名称>` 切换模型",
                output_type=OutputType.MARKDOWN,
            )

        # 切换模型（这里只是示例，实际实现需要更新配置）
        return CommandResult(
            success=True,
            message=f"已切换到模型: **{args}**",
            output_type=OutputType.MARKDOWN,
            data={"action": "switch_model", "model": args},
        )


class MemoryCommand(Command):
    """查看记忆"""

    name = "memory"
    aliases = ["mem"]
    description = "查看用户画像和短期记忆"
    usage = "/memory"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not ctx.workflow or not hasattr(ctx.workflow, 'memory'):
            return CommandResult(
                success=False,
                message="记忆系统未初始化",
                output_type=OutputType.ERROR,
            )

        memory = ctx.workflow.memory
        profile = memory.get_profile()
        short_term = memory.get_short_term_memory()

        lines = ["# 记忆状态\n"]

        # 用户画像
        lines.append("## 用户画像\n")
        if profile:
            for key, value in profile.items():
                lines.append(f"- **{key}:** {value}")
        else:
            lines.append("*暂无用户画像*")

        # 短期记忆
        lines.append("\n## 短期记忆\n")
        if short_term:
            for turn in short_term[-5:]:  # 只显示最近5轮
                role = turn.get("role", "unknown")
                content = turn.get("content", "")[:100]  # 截断长内容
                lines.append(f"- **{role}:** {content}...")
        else:
            lines.append("*暂无对话记录*")

        return CommandResult(
            success=True,
            message="\n".join(lines),
            output_type=OutputType.MARKDOWN,
        )


class ClearMemoryCommand(Command):
    """清空记忆"""

    name = "clear-memory"
    aliases = ["cm"]
    description = "清空短期会话记忆"
    usage = "/clear-memory"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not ctx.workflow or not hasattr(ctx.workflow, 'memory'):
            return CommandResult(
                success=False,
                message="记忆系统未初始化",
                output_type=OutputType.ERROR,
            )

        ctx.workflow.memory.clear_short_term_memory()
        return CommandResult(
            success=True,
            message="✓ 已清空短期记忆",
            output_type=OutputType.SUCCESS,
        )


class BuiltinCommands:
    """内置命令集合"""

    @staticmethod
    def all() -> list[Command]:
        """返回所有内置命令"""
        return [
            HelpCommand(),
            ClearCommand(),
            ExitCommand(),
            ModelCommand(),
            MemoryCommand(),
            ClearMemoryCommand(),
        ]
