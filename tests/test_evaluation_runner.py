from src.evaluation.dataset import EvaluationCase
from src.evaluation.runner import EvaluationRunner


def test_evaluation_runner_writes_reports(tmp_path):
    (tmp_path / "data" / "knowledge_base").mkdir(parents=True)
    (tmp_path / "data" / "knowledge_base" / "rag_basics.md").write_text(
        "RAG uses retrieval and generation with a knowledge base.",
        encoding="utf-8",
    )
    cases = [
        EvaluationCase(
            id="case_1",
            question="Explain RAG",
            expected_keywords=["rag", "retrieval"],
            expected_sources=["rag_basics.md"],
            expected_tools=["search_knowledge_base"],
            expected_agent_sections=["Explanation"],
            memory_seed={"weak_points": ["RAG"]},
        )
    ]

    runner = EvaluationRunner(base_dir=tmp_path)
    report = runner.run_cases(cases)
    paths = runner.write_reports(report)

    assert report.total_cases == 1
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    assert paths["pdf"].exists()

