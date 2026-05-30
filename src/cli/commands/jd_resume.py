"""JD 和简历相关命令"""

from __future__ import annotations

from pathlib import Path

from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


class JDCommand(Command):
    """分析岗位 JD"""

    name = "jd"
    aliases = []
    description = "分析岗位 JD（文本或文件路径）"
    usage = "/jd <JD文本或文件路径>"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message="请提供 JD 文本或文件路径\n\n用法:\n- /jd <JD文本>\n- /jd <文件路径.md>",
                output_type=OutputType.ERROR,
            )

        jd_text = self._load_text(args)
        if not jd_text:
            return CommandResult(
                success=False,
                message=f"无法读取: {args}",
                output_type=OutputType.ERROR,
            )

        try:
            result = ctx.workflow.set_jd(jd_text)
            analysis = result.get("jd_analysis", "分析失败")
            return CommandResult(
                success=True,
                message=f"## JD 分析结果\n\n{analysis}",
                output_type=OutputType.MARKDOWN,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"分析失败: {e}",
                output_type=OutputType.ERROR,
            )

    def _load_text(self, args: str) -> str:
        """加载文本（文件或直接文本）"""
        path = Path(args)
        if path.exists() and path.is_file():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                return ""
        return args


class ResumeCommand(Command):
    """分析简历"""

    name = "resume"
    aliases = []
    description = "分析简历（文本或文件路径）"
    usage = "/resume <简历文本或文件路径>"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message="请提供简历文本或文件路径\n\n用法:\n- /resume <简历文本>\n- /resume <文件路径.md>",
                output_type=OutputType.ERROR,
            )

        resume_text = self._load_text(args)
        if not resume_text:
            return CommandResult(
                success=False,
                message=f"无法读取: {args}",
                output_type=OutputType.ERROR,
            )

        try:
            result = ctx.workflow.set_resume(resume_text)
            analysis = result.get("resume_analysis", "")
            deep_dive = result.get("project_deep_dive", "")
            match = result.get("match_analysis", "")

            sections = ["## 简历分析结果\n"]
            if analysis:
                sections.append(analysis)
            if deep_dive:
                sections.append(f"\n{deep_dive}")
            if match:
                sections.append(f"\n{match}")

            return CommandResult(
                success=True,
                message="\n".join(sections),
                output_type=OutputType.MARKDOWN,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"分析失败: {e}",
                output_type=OutputType.ERROR,
            )

    def _load_text(self, args: str) -> str:
        """加载文本（文件或直接文本）"""
        path = Path(args)
        if path.exists() and path.is_file():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                return ""
        return args


class MatchCommand(Command):
    """分析简历与 JD 匹配度"""

    name = "match"
    aliases = []
    description = "分析简历与 JD 的匹配度"
    usage = "/match"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        try:
            result = ctx.workflow.analyze_match()
            analysis = result.get("match_analysis", "分析失败")
            return CommandResult(
                success=True,
                message=f"## 匹配度分析\n\n{analysis}",
                output_type=OutputType.MARKDOWN,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"分析失败: {e}",
                output_type=OutputType.ERROR,
            )


class JDResumeCommands:
    """JD 和简历命令集合"""

    @staticmethod
    def all() -> list[Command]:
        return [JDCommand(), ResumeCommand(), MatchCommand()]
