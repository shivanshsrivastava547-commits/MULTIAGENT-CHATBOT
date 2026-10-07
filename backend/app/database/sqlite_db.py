# backend/app/database/sqlite_db.py

import sqlite3
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.logger.logger import logger

DB_PATH = "chatbot.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create global messages table used across ALL features
    (chatbot, RAG, research) — single shared DB.
    Called once at startup from main.py lifespan.
    """
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                feature     TEXT DEFAULT 'chat',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content     TEXT NOT NULL,
                feature     TEXT DEFAULT 'chat',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
        """)
    logger.info("[db] Global SQLite tables initialised.")


def create_session(session_id: str, feature: str = 'chat') -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, feature) VALUES (?, ?)",
            (session_id, feature),
        )


def save_message(session_id: str, role: str, content: str, feature: str = 'chat') -> None:
    """
    Persist a single message turn.
    Called AFTER streaming completes so the full content is saved — not mid-stream.
    Works for all features: chat, rag, research.
    """
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, feature) VALUES (?, ?, ?, ?)",
            (session_id, role, content, feature),
        )
    logger.info(f"[db] Saved {role} message | session={session_id} | feature={feature}")


def get_session_messages(session_id: str) -> list[BaseMessage]:
    """Load full conversation history for a session as LangChain messages."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()

    history: list[BaseMessage] = []
    for row in rows:
        if row["role"] == "user":
            history.append(HumanMessage(content=row["content"]))
        else:
            history.append(AIMessage(content=row["content"]))
    return history


def get_all_sessions(feature: str = None) -> list[str]:
    """Return all session IDs, optionally filtered by feature."""
    with get_connection() as conn:
        if feature:
            rows = conn.execute(
                "SELECT session_id FROM sessions WHERE feature = ? ORDER BY created_at DESC",
                (feature,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT session_id FROM sessions ORDER BY created_at DESC"
            ).fetchall()
    return [r["session_id"] for r in rows]
