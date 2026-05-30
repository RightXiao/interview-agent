from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from src.documents.loaders import load_document
from src.rag.splitter import split_documents


class VectorStore:
    """Unified storage: Chroma + embeddings when configured, keyword fallback otherwise."""

    def __init__(
        self,
        persist_dir: Path | str,
        embedding_model: str = "",
        base_url: str = "",
        api_key: str = "",
    ) -> None:
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._json_path = self._persist_dir / "local_index.json"
        self._use_embeddings = bool(embedding_model and base_url and api_key)
        self._collection: Any = None
        self._embeddings: Any = None
        if self._use_embeddings:
            self._init_chroma(embedding_model, base_url, api_key)

    def _init_chroma(self, embedding_model: str, base_url: str, api_key: str) -> None:
        import chromadb
        from langchain_openai import OpenAIEmbeddings

        self._client = chromadb.PersistentClient(path=str(self._persist_dir / "chroma"))
        self._embeddings = OpenAIEmbeddings(
            model=embedding_model,
            base_url=base_url,
            api_key=api_key,
            check_embedding_ctx_length=False,
            chunk_size=10,
        )
        self._collection = self._client.get_or_create_collection("knowledge_base")

    def add(self, chunks: list) -> int:
        if not chunks:
            return 0
        if self._use_embeddings:
            return self._add_chroma(chunks)
        return self._add_json(chunks)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if self._use_embeddings:
            return self._search_chroma(query, top_k)
        entries = self._read_json()
        return _keyword_retrieve(entries, query, top_k)

    def read_all(self) -> list[dict]:
        if self._use_embeddings:
            return self._read_all_chroma()
        return self._read_json()

    def clear(self) -> None:
        if self._use_embeddings:
            try:
                self._client.delete_collection("knowledge_base")
            except Exception:
                pass
            self._collection = self._client.get_or_create_collection("knowledge_base")
        else:
            self._write_json([])

    def _add_chroma(self, chunks: list) -> int:
        texts = [chunk.text for chunk in chunks]
        metadatas = [{k: str(v) if v is not None else "" for k, v in chunk.metadata.items()} for chunk in chunks]
        ids = [chunk.metadata.get("chunk_id", str(i)) for i, chunk in enumerate(chunks)]
        vectors = self._embeddings.embed_documents(texts)
        self._collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
        return len(chunks)

    def _search_chroma(self, query: str, top_k: int) -> list[dict]:
        query_vector = self._embeddings.embed_query(query)
        results = self._collection.query(query_embeddings=[query_vector], n_results=top_k)
        entries: list[dict] = []
        if not results["ids"] or not results["ids"][0]:
            return entries
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            entry = {"text": results["documents"][0][i], "metadata": metadata}
            page = metadata.get("page", "")
            if page and page.isdigit():
                entry["metadata"]["page"] = int(page)
            elif page == "":
                entry["metadata"].pop("page", None)
            entries.append(entry)
        return entries

    def _read_all_chroma(self) -> list[dict]:
        try:
            results = self._collection.get()
        except Exception:
            return []
        entries: list[dict] = []
        if not results["ids"]:
            return entries
        for i in range(len(results["ids"])):
            metadata = results["metadatas"][i] if results["metadatas"] else {}
            entry = {"text": results["documents"][i], "metadata": metadata}
            page = metadata.get("page", "")
            if page and page.isdigit():
                entry["metadata"]["page"] = int(page)
            elif page == "":
                entry["metadata"].pop("page", None)
            entries.append(entry)
        return entries

    def _add_json(self, chunks: list) -> int:
        entries = [{"text": chunk.text, "metadata": chunk.metadata} for chunk in chunks]
        existing = self._read_json()
        existing.extend(entries)
        self._write_json(existing)
        return len(entries)

    def _read_json(self) -> list[dict[str, Any]]:
        if not self._json_path.exists():
            return []
        try:
            return json.loads(self._json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _write_json(self, entries: list[dict[str, Any]]) -> None:
        self._json_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def _keyword_retrieve(entries: list[dict], query: str, top_k: int) -> list[dict]:
    query_terms = _terms(query)
    scored = []
    for entry in entries:
        text_terms = _terms(entry.get("text", ""))
        score = sum((query_terms & text_terms).values())
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]


def _terms(text: str) -> Counter:
    return Counter(re.findall(r"[A-Za-z0-9_一-鿿]+", text.lower()))


def import_document(source_path: Path | str, uploads_dir: Path | str) -> Path:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Import file does not exist: {source}")
    if source.suffix.lower() not in {".md", ".txt", ".pdf"}:
        raise ValueError("Only .md, .txt, and .pdf files are supported.")
    target_dir = Path(uploads_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target


def build_local_index(
    knowledge_dirs: list[Path | str],
    store: VectorStore,
    chunk_size: int = 800,
    overlap: int = 120,
) -> int:
    """Load documents from knowledge_dirs, split into chunks, and add to the vector store."""
    documents = []
    for directory in knowledge_dirs:
        root = Path(directory)
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".pdf"}:
                documents.extend(load_document(path))

    chunks = split_documents(documents, chunk_size=chunk_size, overlap=overlap)
    store.clear()
    return store.add(chunks)
