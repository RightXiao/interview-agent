from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = {
    "target_role": "",
    "tech_stack": [],
    "weak_points": [],
    "learning_goals": [],
    "recent_topics": [],
}


class MemoryStore:
    def __init__(self, base_dir: Path | str, max_turns: int = 8) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.session_path = self.base_dir / "session.json"
        self.profile_path = self.base_dir / "profile.json"
        self.sessions_dir = self.base_dir / "sessions"
        self.max_turns = max_turns

    def get_short_term_memory(self) -> list[dict[str, str]]:
        data = self._read_json(self.session_path, {"turns": []})
        return data.get("turns", [])

    def add_turn(self, role: str, content: str) -> None:
        turns = self.get_short_term_memory()
        turns.append({"role": role, "content": content})
        turns = turns[-self.max_turns :]
        self._write_json(self.session_path, {"turns": turns})

    def clear_short_term_memory(self) -> None:
        self._write_json(self.session_path, {"turns": []})

    def get_profile(self) -> dict[str, Any]:
        profile = DEFAULT_PROFILE.copy()
        profile.update(self._read_json(self.profile_path, {}))
        for key in ["tech_stack", "weak_points", "learning_goals", "recent_topics"]:
            profile.setdefault(key, [])
        return profile

    def update_profile(self, updates: dict[str, Any]) -> None:
        profile = self.get_profile()
        for key, value in updates.items():
            if isinstance(value, list):
                current = profile.get(key, [])
                if not isinstance(current, list):
                    current = []
                profile[key] = _dedupe([*current, *value])
            elif value:
                profile[key] = value
        self._write_json(self.profile_path, profile)

    def _read_json(self, path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_session_snapshot(self, label: str = "session") -> str:
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{ts}_{label}"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "id": session_id,
            "timestamp": datetime.now().isoformat(),
            "turns": self.get_short_term_memory(),
            "profile": self.get_profile(),
        }
        path = self.sessions_dir / f"{session_id}.json"
        self._write_json(path, snapshot)
        return session_id

    def list_sessions(self) -> list[dict[str, Any]]:
        if not self.sessions_dir.exists():
            return []
        sessions = []
        for path in sorted(self.sessions_dir.glob("*.json"), reverse=True):
            data = self._read_json(path, {})
            if data:
                turns = data.get("turns", [])
                preview = ""
                for turn in turns:
                    if turn.get("role") == "user":
                        preview = turn.get("content", "")[:60]
                        break
                sessions.append({
                    "id": data.get("id", path.stem),
                    "timestamp": data.get("timestamp", ""),
                    "turn_count": len(turns),
                    "preview": preview,
                })
        return sessions

    def load_session(self, session_id: str) -> bool:
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return False
        data = self._read_json(path, {})
        if not data:
            return False
        self._write_json(self.session_path, {"turns": data.get("turns", [])})
        profile = data.get("profile")
        if profile:
            self._write_json(self.profile_path, profile)
        return True


def _dedupe(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result

