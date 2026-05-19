from __future__ import annotations

from dataclasses import dataclass

from src.config import AppConfig


class LLMClientError(RuntimeError):
    """Raised when the configured LLM client cannot be used."""


@dataclass
class OpenAICompatibleClient:
    config: AppConfig

    def generate(self, prompt: str) -> str:
        missing = self.config.validate_llm()
        if missing:
            raise LLMClientError(f"Missing LLM configuration: {', '.join(missing)}")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise LLMClientError("Install langchain-openai to use real model calls.") from exc

        model = ChatOpenAI(
            model=self.config.llm_model,
            api_key=self.config.llm_api_key,
            base_url=self.config.llm_base_url,
        )
        response = model.invoke(prompt)
        return getattr(response, "content", str(response))

