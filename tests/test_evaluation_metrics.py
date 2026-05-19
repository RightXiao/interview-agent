from src.evaluation.metrics import (
    score_keyword_coverage,
    score_memory_hit_rate,
    score_multi_agent_completeness,
    score_source_precision,
    score_source_recall,
    score_tool_success_rate,
)


def test_keyword_coverage_scores_expected_terms():
    score = score_keyword_coverage("RAG uses retrieval and generation", ["retrieval", "generation"])
    assert score == 1.0


def test_source_precision_and_recall_match_expected_sources():
    retrieved = ["data/knowledge_base/rag_basics.md", "data/knowledge_base/tool_calling.md"]
    expected = ["rag_basics.md"]

    assert score_source_precision(retrieved, expected) == 0.5
    assert score_source_recall(retrieved, expected) == 1.0


def test_agent_metrics_score_observable_behavior():
    answer = "Explanation:\nRAG helps AI Agent Engineer candidates.\nInterview follow-ups:\nReview advice:"

    assert score_tool_success_rate(["search_knowledge_base"], ["search_knowledge_base"]) == 1.0
    assert score_memory_hit_rate(answer, {"target_role": "AI Agent Engineer"}) == 1.0
    assert score_multi_agent_completeness(answer, ["Explanation", "Interview follow-ups", "Review advice"]) == 1.0

