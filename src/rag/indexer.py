from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.documents.loaders import load_document
from src.rag.splitter import split_documents


class LocalKnowledgeIndex:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def write(self, entries: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))


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
    index_path: Path | str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> int:
    documents = []
    for directory in knowledge_dirs:
        root = Path(directory)
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".pdf"}:
                documents.extend(load_document(path))

    chunks = split_documents(documents, chunk_size=chunk_size, overlap=overlap)
    entries = [{"text": chunk.text, "metadata": chunk.metadata} for chunk in chunks]
    LocalKnowledgeIndex(index_path).write(entries)
    return len(entries)

