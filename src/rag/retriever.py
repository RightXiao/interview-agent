from __future__ import annotations

from src.rag.indexer import VectorStore


def retrieve_from_store(
    store: VectorStore,
    query: str,
    top_k: int = 4,
) -> list[dict]:
    """Retrieve top_k chunks from the vector store for a given query."""
    return store.search(query, top_k)


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
