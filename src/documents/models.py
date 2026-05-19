from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadedDocument:
    source_path: str
    source_type: str
    text: str
    page: int | None = None


@dataclass(frozen=True)
class TextChunk:
    text: str
    metadata: dict

