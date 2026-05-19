from __future__ import annotations

from pathlib import Path

from src.evaluation.dataset import load_evaluation_cases
from src.evaluation.runner import EvaluationRunner


def main() -> None:
    base_dir = Path.cwd()
    dataset_path = base_dir / "evals" / "datasets" / "interview_agent_eval.json"
    cases = load_evaluation_cases(dataset_path)
    runner = EvaluationRunner(base_dir=base_dir)
    report = runner.run_cases(cases)
    paths = runner.write_reports(report)
    print(f"Evaluation complete: {report.passed_cases}/{report.total_cases} passed")
    print(f"Markdown: {paths['markdown']}")
    print(f"JSON: {paths['json']}")
    print(f"PDF: {paths['pdf']}")


if __name__ == "__main__":
    main()

