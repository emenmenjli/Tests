import sqlite3
import json
from datetime import datetime
from app.config import Config


class Memory:
    def __init__(self):
        self.db_path = Config.DB_PATH
        Config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    tool_name TEXT NOT NULL,
                    args TEXT,
                    result TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
            """)

    def add_message(self, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (role, content, timestamp) VALUES (?, ?, ?)",
                (role, content, datetime.now().isoformat()),
            )

    def get_recent(self, limit: int = None) -> list[dict]:
        if limit is None:
            limit = Config.MAX_HISTORY
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        messages = [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        return messages

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM tool_calls")

    def add_tool_call(self, tool_name: str, args: dict, result: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tool_calls (tool_name, args, result, timestamp) VALUES (?, ?, ?, ?)",
                (tool_name, json.dumps(args), str(result)[:2000], datetime.now().isoformat()),
            )
