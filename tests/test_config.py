from src.config import AppConfig


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "key")
    monkeypatch.setenv("LLM_MODEL", "model")
    monkeypatch.setenv("EMBEDDING_MODEL", "embed")

    config = AppConfig.from_env()

    assert config.llm_base_url == "https://api.example.com/v1"
    assert config.llm_api_key == "key"
    assert config.llm_model == "model"
    assert config.embedding_model == "embed"
    assert config.memory_max_turns == 8

