"""
Chat plugin service with emotion tracking.
Stores sessions, messages and emotion stream in SQLite.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
import sqlite3
import time

SCHEMA = {
    "chat_sessions": """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            topic TEXT,
            created_at INTEGER NOT NULL
        );
    """,
    "chat_messages": """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            emotion TEXT,
            intensity REAL,
            created_at INTEGER NOT NULL
        );
    """,
    "emotion_stream": """
        CREATE TABLE IF NOT EXISTS emotion_stream (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            emotion TEXT NOT NULL,
            intensity REAL NOT NULL,
            source TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
    """
}


class ChatService:
    def __init__(self, db_path: str = "modernreader.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        conn = self._connect()
        cur = conn.cursor()
        for ddl in SCHEMA.values():
            cur.execute(ddl)
        conn.commit()
        conn.close()

    def start_session(self, user_id: str, topic: Optional[str] = None) -> int:
        ts = int(time.time())
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_sessions (user_id, topic, created_at) VALUES (?, ?, ?)",
            (user_id, topic, ts)
        )
        session_id = cur.lastrowid
        conn.commit()
        conn.close()
        return int(session_id) if session_id is not None else 0

    def handle_message(self, session_id: int, user_id: str, text: str, emotion: Optional[str], intensity: Optional[float]) -> Dict[str, Any]:
        ts = int(time.time())
        conn = self._connect()
        cur = conn.cursor()
        # Save user message
        cur.execute(
            "INSERT INTO chat_messages (session_id, user_id, role, text, emotion, intensity, created_at) VALUES (?, ?, 'user', ?, ?, ?, ?)",
            (session_id, user_id, text, emotion, intensity, ts)
        )
        # Simple AI reply (placeholder). In production, call LLM here.
        reply_text = self._ai_reply(text, emotion)
        cur.execute(
            "INSERT INTO chat_messages (session_id, user_id, role, text, created_at) VALUES (?, ?, 'assistant', ?, ?)",
            (session_id, user_id, reply_text, ts)
        )
        conn.commit()
        conn.close()
        return {"reply": reply_text, "timestamp": ts}

    def get_history(self, session_id: int, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT role, text, emotion, intensity, created_at FROM chat_messages WHERE session_id=? AND user_id=? ORDER BY id DESC LIMIT ?",
            (session_id, user_id, limit)
        )
        rows = cur.fetchall()
        conn.close()
        rows.reverse()
        return [
            {"role": r[0], "text": r[1], "emotion": r[2], "intensity": r[3], "timestamp": r[4]}
            for r in rows
        ]

    def push_emotion(self, session_id: int, user_id: str, emotion: str, intensity: float, source: str) -> None:
        ts = int(time.time())
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO emotion_stream (session_id, user_id, emotion, intensity, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, user_id, emotion, intensity, source, ts)
        )
        conn.commit()
        conn.close()

    def _ai_reply(self, user_text: str, emotion: Optional[str]) -> str:
        # Minimal sentiment-aware reply
        if not emotion:
            return f"我在這裡陪你聊聊：{user_text}"
        mapping = {
            "happy": "很開心聽到你的分享！",
            "sad": "聽起來你有些低落，我在。",
            "excited": "太棒了！讓我們延續這股動力。",
            "calm": "保持平靜很好，慢慢聊。",
            "surprised": "哇，這真是出乎意料！",
            "neutral": "我懂了，請繼續。"
        }
        prefix = mapping.get(emotion, "我在這裡陪你：")
        return f"{prefix} 你說：{user_text}"
