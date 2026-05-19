from src.memory.store import MemoryStore


def test_memory_store_keeps_recent_turns(tmp_path):
    store = MemoryStore(tmp_path, max_turns=2)

    store.add_turn("user", "one")
    store.add_turn("assistant", "two")
    store.add_turn("user", "three")

    turns = store.get_short_term_memory()
    assert [turn["content"] for turn in turns] == ["two", "three"]


def test_profile_update_merges_lists(tmp_path):
    store = MemoryStore(tmp_path)
    store.update_profile({"weak_points": ["RAG"]})
    store.update_profile({"weak_points": ["RAG", "tools"]})

    profile = store.get_profile()
    assert profile["weak_points"] == ["RAG", "tools"]

