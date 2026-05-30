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


def test_save_and_list_sessions(tmp_path):
    store = MemoryStore(tmp_path, max_turns=8)
    store.add_turn("user", "hello")
    store.add_turn("assistant", "hi there")

    session_id = store.save_session_snapshot("test")
    assert "test" in session_id

    sessions = store.list_sessions()
    assert len(sessions) == 1
    assert sessions[0]["id"] == session_id
    assert sessions[0]["turn_count"] == 2
    assert sessions[0]["preview"] == "hello"


def test_load_session(tmp_path):
    store = MemoryStore(tmp_path, max_turns=8)
    store.add_turn("user", "original question")
    store.add_turn("assistant", "original answer")

    session_id = store.save_session_snapshot("backup")

    store.add_turn("user", "new question")
    store.add_turn("assistant", "new answer")
    assert len(store.get_short_term_memory()) == 4

    assert store.load_session(session_id) is True
    turns = store.get_short_term_memory()
    assert len(turns) == 2
    assert turns[0]["content"] == "original question"


def test_load_nonexistent_session(tmp_path):
    store = MemoryStore(tmp_path)
    assert store.load_session("nonexistent") is False

