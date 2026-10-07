# backend/app/chatbot/service.py

from langchain_core.messages import HumanMessage
from app.chatbot.graph import chatbot
from app.database.sqlite_db import save_message, create_session
from app.logger.logger import logger
from typing import Iterator


def _make_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }


def get_chat_response(message: str, thread_id: str) -> str:
    """Standard invoke — saves both turns to global SQLite after response."""
    logger.info(f"[service] invoke | thread={thread_id}")
    create_session(thread_id, feature='chat')
    config = _make_config(thread_id)
    try:
        result = chatbot.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )
    except Exception as e:
        logger.error(f"[service] invoke error: {e}")
        raise

    ai_reply: str = result["messages"][-1].content

    # Persist both turns to global SQLite
    save_message(thread_id, "user",      message,  feature='chat')
    save_message(thread_id, "assistant", ai_reply, feature='chat')

    return ai_reply


def stream_chat_response(message: str, thread_id: str) -> Iterator[str]:
    """
    Streaming invoke — yields tokens as they arrive.
    Saves FULL message to global SQLite only after stream completes.
    This way partial/incomplete messages are never saved.
    """
    logger.info(f"[service] stream | thread={thread_id}")
    create_session(thread_id, feature='chat')
    config = _make_config(thread_id)

    full_response = ""

    try:
        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="messages",
        ):
            if message_chunk.content:
                full_response += message_chunk.content
                yield message_chunk.content

        # Stream finished — now save both turns to global SQLite
        save_message(thread_id, "user",      message,       feature='chat')
        save_message(thread_id, "assistant", full_response, feature='chat')
        logger.info(f"[service] stream complete + saved | thread={thread_id}")

    except Exception as e:
        logger.error(f"[service] stream error: {e}")
        raise
