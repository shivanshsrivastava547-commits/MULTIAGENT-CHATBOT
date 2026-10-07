# backend/app/chatbot/graph.py

import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.chatbot.nodes import chat_node
from app.chatbot.state import ChatState
from app.config.settings import settings
from app.logger.logger import logger


# ── Checkpointer ───────────────────────────────────────────────────────────
# check_same_thread=False is required for FastAPI (multi-threaded)
conn = sqlite3.connect(settings.SQLITE_DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)


# ── Graph ──────────────────────────────────────────────────────────────────
def build_graph():
    """
    Minimal correct graph:
        [START] → chat_node → [END]

    Memory is handled entirely by SqliteSaver.
    Each request passes thread_id via config — LangGraph automatically
    loads that thread's history before the node runs and saves state after.
    """
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_edge(START, "chat_node")
    graph.add_edge("chat_node", END)

    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("[graph] Chatbot graph compiled with SqliteSaver.")
    return compiled


# Singleton — import this everywhere
chatbot = build_graph()


# ── Thread utility ─────────────────────────────────────────────────────────
def retrieve_all_threads() -> list[str]:
    """Return all unique thread_ids stored in the checkpointer."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)
