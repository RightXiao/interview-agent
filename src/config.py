from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    embedding_model: str
    memory_max_turns: int = 8
    rag_top_k: int = 4
    pdf_font_path: str | None = None
    base_dir: Path = Path(".")

    @classmethod
    def from_env(cls, base_dir: Path | str = ".") -> "AppConfig":
        _load_dotenv_if_available()
        return cls(
            llm_base_url=os.getenv("LLM_BASE_URL", ""),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", ""),
            embedding_model=os.getenv("EMBEDDING_MODEL", ""),
            memory_max_turns=int(os.getenv("MEMORY_MAX_TURNS", "8")),
            rag_top_k=int(os.getenv("RAG_TOP_K", "4")),
            pdf_font_path=os.getenv("PDF_FONT_PATH") or None,
            base_dir=Path(base_dir),
        )

    def validate_llm(self) -> list[str]:
        missing = []
        if not self.llm_base_url:
            missing.append("LLM_BASE_URL")
        if not self.llm_api_key:
            missing.append("LLM_API_KEY")
        if not self.llm_model:
            missing.append("LLM_MODEL")
        return missing

