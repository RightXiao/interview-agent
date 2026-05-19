from src.agents.graph import AgentWorkflow


class FakeLLM:
    def generate(self, prompt: str) -> str:
        return "fake model response"


def test_workflow_returns_answer(tmp_path):
    workflow = AgentWorkflow(base_dir=tmp_path, llm=FakeLLM())

    result = workflow.run("Explain tool calling")

    assert "tool calling" in result.answer.lower()
    assert result.answer

