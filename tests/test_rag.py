from src.documents.models import LoadedDocument, TextChunk
from src.rag.indexer import VectorStore
from src.rag.retriever import retrieve_from_store
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


def test_vector_store_retrieves_matching_chunk(tmp_path):
    store = VectorStore(persist_dir=tmp_path)
    chunk = TextChunk(
        text="LangGraph coordinates agent workflows.",
        metadata={"source_path": "agent.md", "source_type": "md", "page": None},
    )
    store.add([chunk])

    results = retrieve_from_store(store, "agent workflows", top_k=1)

    assert results[0]["metadata"]["source_path"] == "agent.md"
