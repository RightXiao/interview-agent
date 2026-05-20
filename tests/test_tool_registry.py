from src.memory.store import MemoryStore
from src.rag.indexer import VectorStore
from src.tools.registry import ToolRegistry


def test_tool_registry_calls_registered_tool():
    registry = ToolRegistry()
    registry.register("echo", lambda value: value)

    assert registry.call("echo", "hello") == "hello"


def test_default_tools_are_registered(tmp_path):
    store = VectorStore(persist_dir=tmp_path / "vector_store")
    memory = MemoryStore(tmp_path / "memory")
    registry = ToolRegistry.with_defaults(store, memory)

    assert registry.has("read_user_profile")
    assert registry.has("generate_study_plan")

