from __future__ import annotations

import re
from collections import Counter

from src.rag.indexer import LocalKnowledgeIndex


def retrieve_from_local_index(
    index: LocalKnowledgeIndex,
    query: str,
    top_k: int = 4,
) -> list[dict]:
    entries = index.read()
    query_terms = _terms(query)
    scored = []
    for entry in entries:
        text_terms = _terms(entry.get("text", ""))
        score = sum((query_terms & text_terms).values())
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def format_sources(results: list[dict]) -> list[str]:
    sources = []
    for result in results:
        metadata = result.get("metadata", {})
        source = metadata.get("source_path", "unknown")
        page = metadata.get("page")
        label = f"{source} page {page}" if page else source
        if label not in sources:
            sources.append(label)
    return sources


def _terms(text: str) -> Counter:
    return Counter(re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", text.lower()))

