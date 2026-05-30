"""文档命令 - import, export, reindex 等"""

from __future__ import annotations

from pathlib import Path

from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


class ImportCommand(Command):
    """导入文档"""

    name = "import"
    aliases = ["i"]
    description = "导入文档到知识库（支持 .md / .txt / .pdf）"
    usage = "/import <文件路径>"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message="请指定文件路径\n\n用法: /import <文件路径>",
                output_type=OutputType.ERROR,
            )

        source = Path(args)
        if not source.exists():
            return CommandResult(
                success=False,
                message=f"文件不存在: {args}",
                output_type=OutputType.ERROR,
            )

        # 检查文件类型
        allowed_types = {".md", ".txt", ".pdf"}
        if source.suffix.lower() not in allowed_types:
            return CommandResult(
                success=False,
                message=f"不支持的文件类型: {source.suffix}\n\n支持的类型: {', '.join(allowed_types)}",
                output_type=OutputType.ERROR,
            )

        try:
            from src.rag.indexer import build_local_index, import_document

            uploads_dir = ctx.workflow.base_dir / "data" / "uploads"
            target = import_document(source, uploads_dir)

            # 重建索引
            if ctx.workflow and hasattr(ctx.workflow, 'store'):
                try:
                    count = build_local_index(
                        [ctx.workflow.base_dir / "data" / "knowledge_base", uploads_dir],
                        ctx.workflow.store,
                    )
                    return CommandResult(
                        success=True,
                        message=f"✓ 已导入文档: **{target.name}**\n\n已索引 {count} 个文本块",
                        output_type=OutputType.SUCCESS,
                    )
                except Exception as e:
                    return CommandResult(
                        success=True,
                        message=f"✓ 已导入文档: **{target.name}**\n\n⚠ 索引重建失败: {e}",
                        output_type=OutputType.WARNING,
                    )

            return CommandResult(
                success=True,
                message=f"✓ 已导入文档: **{target.name}**",
                output_type=OutputType.SUCCESS,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"导入失败: {e}",
                output_type=OutputType.ERROR,
            )


class ExportCommand(Command):
    """导出内容"""

    name = "export"
    aliases = ["e"]
    description = "导出回答或学习计划为 PDF"
    usage = "/export <answer|plan> <输出路径>"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not args:
            return CommandResult(
                success=False,
                message="请指定导出类型和路径\n\n用法:\n- /export answer <路径>\n- /export plan <路径>",
                output_type=OutputType.ERROR,
            )

        parts = args.split(None, 1)
        if len(parts) < 2:
            return CommandResult(
                success=False,
                message="请指定输出路径\n\n用法:\n- /export answer <路径>\n- /export plan <路径>",
                output_type=OutputType.ERROR,
            )

        export_type, output_path = parts

        if export_type == "answer":
            return self._export_answer(output_path, ctx)
        elif export_type == "plan":
            return self._export_plan(output_path, ctx)
        else:
            return CommandResult(
                success=False,
                message=f"未知导出类型: {export_type}\n\n支持的类型: answer, plan",
                output_type=OutputType.ERROR,
            )

    def _export_answer(self, output_path: str, ctx: CommandContext) -> CommandResult:
        """导出回答"""
        if not ctx.latest_answer:
            return CommandResult(
                success=False,
                message="没有可导出的回答",
                output_type=OutputType.ERROR,
            )

        try:
            from src.documents.exporters import export_answer_to_pdf

            font_path = ctx.config.pdf_font_path if ctx.config else None
            path = export_answer_to_pdf(
                title="Agent Interview Coach Answer",
                content=ctx.latest_answer,
                sources=ctx.latest_sources,
                output_path=ctx.workflow.base_dir / output_path,
                font_path=font_path,
            )
            return CommandResult(
                success=True,
                message=f"✓ 已导出回答到: **{path}**",
                output_type=OutputType.SUCCESS,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"导出失败: {e}",
                output_type=OutputType.ERROR,
            )

    def _export_plan(self, output_path: str, ctx: CommandContext) -> CommandResult:
        """导出学习计划"""
        if not ctx.latest_study_plan:
            return CommandResult(
                success=False,
                message="没有可导出的学习计划",
                output_type=OutputType.ERROR,
            )

        try:
            from src.documents.exporters import export_study_plan_to_pdf

            font_path = ctx.config.pdf_font_path if ctx.config else None
            path = export_study_plan_to_pdf(
                plan=ctx.latest_study_plan,
                output_path=ctx.workflow.base_dir / output_path,
                font_path=font_path,
            )
            return CommandResult(
                success=True,
                message=f"✓ 已导出学习计划到: **{path}**",
                output_type=OutputType.SUCCESS,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"导出失败: {e}",
                output_type=OutputType.ERROR,
            )


class ReindexCommand(Command):
    """重建索引"""

    name = "reindex"
    aliases = ["ri"]
    description = "重建本地知识索引"
    usage = "/reindex"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not ctx.workflow or not hasattr(ctx.workflow, 'store'):
            return CommandResult(
                success=False,
                message="知识库未初始化",
                output_type=OutputType.ERROR,
            )

        try:
            from src.rag.indexer import build_local_index

            count = build_local_index(
                [ctx.workflow.base_dir / "data" / "knowledge_base", ctx.workflow.base_dir / "data" / "uploads"],
                ctx.workflow.store,
            )
            return CommandResult(
                success=True,
                message=f"✓ 已重建知识索引，索引 {count} 个文本块",
                output_type=OutputType.SUCCESS,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"索引重建失败: {e}",
                output_type=OutputType.ERROR,
            )


class TemplateCommand(Command):
    """切换面试模板"""

    name = "template"
    aliases = ["t"]
    description = "查看或切换面试场景模板"
    usage = "/template [模板名称]"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        if not ctx.workflow:
            return CommandResult(
                success=False,
                message="工作流未初始化",
                output_type=OutputType.ERROR,
            )

        if not args:
            # 显示可用模板
            from src.agents.templates import list_templates

            templates = list_templates()
            current = ctx.workflow.template.name if ctx.workflow.template else "none"
            if not templates:
                return CommandResult(
                    success=True,
                    message="没有可用的模板",
                    output_type=OutputType.TEXT,
                )

            lines = ["# 可用模板\n"]
            for t in templates:
                marker = " (active)" if t.name == current else ""
                lines.append(f"- **{t.name}** {t.label}{marker}")
                lines.append(f"  {t.description}")

            return CommandResult(
                success=True,
                message="\n".join(lines),
                output_type=OutputType.MARKDOWN,
            )

        # 切换模板
        from src.agents.templates import get_template

        template = get_template(args)
        if not template:
            return CommandResult(
                success=False,
                message=f"未知模板: {args}\n\n使用 `/template` 查看可用模板",
                output_type=OutputType.ERROR,
            )

        ctx.workflow.set_template(template)
        return CommandResult(
            success=True,
            message=f"✓ 已切换到模板: **{template.label}** — {template.description}",
            output_type=OutputType.SUCCESS,
        )


class DocumentCommands:
    """文档命令集合"""

    @staticmethod
    def all() -> list[Command]:
        """返回所有文档命令"""
        return [
            ImportCommand(),
            ExportCommand(),
            ReindexCommand(),
            TemplateCommand(),
        ]
