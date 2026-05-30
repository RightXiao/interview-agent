"""会话管理 - 历史记录、恢复、上下文"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionInfo:
    """会话信息"""
    id: str
    created_at: str
    updated_at: str
    preview: str = ""
    data: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """会话管理器"""

    def __init__(self, session_dir: str | Path = "data/sessions") -> None:
        self._session_dir = Path(session_dir)
        self._session_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, data: dict[str, Any] | None = None) -> str:
        """创建新会话

        Args:
            data: 初始数据

        Returns:
            会话 ID
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:6]
        now = datetime.now().isoformat()

        session_data = {
            "id": session_id,
            "created_at": now,
            "updated_at": now,
            "data": data or {},
            "turns": [],
        }

        self._save_session(session_id, session_data)
        return session_id

    def save_session(self, session_id: str, data: dict[str, Any]) -> None:
        """保存会话数据

        Args:
            session_id: 会话 ID
            data: 会话数据
        """
        session_file = self._session_dir / f"{session_id}.json"
        if session_file.exists():
            existing = json.loads(session_file.read_text(encoding="utf-8"))
            existing.update(data)
            existing["updated_at"] = datetime.now().isoformat()
            self._save_session(session_id, existing)
        else:
            data["id"] = session_id
            data["created_at"] = datetime.now().isoformat()
            data["updated_at"] = datetime.now().isoformat()
            self._save_session(session_id, data)

    def load_session(self, session_id: str) -> dict[str, Any] | None:
        """加载会话数据

        Args:
            session_id: 会话 ID

        Returns:
            会话数据，不存在返回 None
        """
        session_file = self._session_dir / f"{session_id}.json"
        if not session_file.exists():
            return None

        return json.loads(session_file.read_text(encoding="utf-8"))

    def list_sessions(self) -> list[SessionInfo]:
        """列出所有会话

        Returns:
            会话信息列表
        """
        sessions = []
        for session_file in sorted(self._session_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                turns = data.get("turns", [])
                preview = ""
                if turns:
                    last_turn = turns[-1]
                    preview = last_turn.get("content", "")[:50]

                sessions.append(SessionInfo(
                    id=data.get("id", session_file.stem),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    preview=preview,
                    data=data.get("data", {}),
                ))
            except (json.JSONDecodeError, KeyError):
                continue

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """删除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否成功删除
        """
        session_file = self._session_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            return True
        return False

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        """添加对话轮次

        Args:
            session_id: 会话 ID
            role: 角色（user/assistant）
            content: 内容
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return

        turns = session_data.get("turns", [])
        turns.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        session_data["turns"] = turns
        self.save_session(session_id, session_data)

    def get_turns(self, session_id: str) -> list[dict[str, str]]:
        """获取对话轮次

        Args:
            session_id: 会话 ID

        Returns:
            对话轮次列表
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return []
        return session_data.get("turns", [])

    def _save_session(self, session_id: str, data: dict[str, Any]) -> None:
        """保存会话到文件"""
        session_file = self._session_dir / f"{session_id}.json"
        session_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
