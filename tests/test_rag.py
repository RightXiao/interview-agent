from src.documents.models import LoadedDocument
from src.rag.indexer import LocalKnowledgeIndex
from src.rag.retriever import retrieve_from_local_index
from src.rag.splitter import split_documents


def test_splitter_preserves_pdf_page_metadata():
    docs = [
        LoadedDocument(
            source_path="a.pdf",
            source_type="pdf",
            text="RAG retrieves context before generation.",
            page=2,
        )
    ]

    chunks = split_documents(docs, chunk_size=20, overlap=5)

    assert chunks[0].metadata["page"] == 2
    assert chunks[0].metadata["source_type"] == "pdf"


def test_local_index_retrieves_matching_chunk(tmp_path):
    index = LocalKnowledgeIndex(tmp_path / "index.json")
    index.write(
        [
            {
                "text": "LangGraph coordinates agent workflows.",
                "metadata": {"source_path": "agent.md", "source_type": "md", "page": None},
            }
        ]
    )

    results = retrieve_from_local_index(index, "agent workflows", top_k=1)

    assert results[0]["metadata"]["source_path"] == "agent.md"

