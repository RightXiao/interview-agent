"""评估命令 - eval 等"""

from __future__ import annotations

from pathlib import Path

from src.cli.commands.base import Command, CommandContext, CommandResult, OutputType


class EvalCommand(Command):
    """运行评估"""

    name = "eval"
    aliases = []
    description = "运行评估并输出报告"
    usage = "/eval"

    def execute(self, args: str, ctx: CommandContext) -> CommandResult:
        try:
            from src.evaluation.dataset import load_evaluation_cases
            from src.evaluation.runner import EvaluationRunner

            # 加载评估数据集
            dataset_path = ctx.workflow.base_dir / "evals" / "datasets" / "interview_agent_eval.json"
            if not dataset_path.exists():
                return CommandResult(
                    success=False,
                    message=f"评估数据集不存在: {dataset_path}",
                    output_type=OutputType.ERROR,
                )

            cases = load_evaluation_cases(dataset_path)
            if not cases:
                return CommandResult(
                    success=False,
                    message="评估数据集为空",
                    output_type=OutputType.ERROR,
                )

            # 运行评估
            runner = EvaluationRunner(base_dir=ctx.workflow.base_dir)
            report = runner.run_cases(cases)
            paths = runner.write_reports(report)

            # 构建摘要
            total = report.total_cases
            passed = report.passed_cases
            rate = (passed / total * 100) if total > 0 else 0.0

            lines = [
                "# 评估完成\n",
                f"**通过率:** {passed}/{total} ({rate:.1f}%)\n",
                "## 报告位置\n",
                f"- `{paths['markdown']}`",
                f"- `{paths['json']}`",
                f"- `{paths['pdf']}`",
            ]

            return CommandResult(
                success=True,
                message="\n".join(lines),
                output_type=OutputType.MARKDOWN,
            )

        except ImportError:
            return CommandResult(
                success=False,
                message="评估模块未安装",
                output_type=OutputType.ERROR,
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"评估失败: {e}",
                output_type=OutputType.ERROR,
            )


class EvaluationCommands:
    """评估命令集合"""

    @staticmethod
    def all() -> list[Command]:
        """返回所有评估命令"""
        return [
            EvalCommand(),
        ]
