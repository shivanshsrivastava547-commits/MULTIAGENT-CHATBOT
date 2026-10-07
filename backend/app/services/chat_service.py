from app.chatbot.service import get_chat_response
from app.chatbot.service import stream_chat_response as _stream_chat_response
from typing import Iterator


def chat_response(message: str, thread_id: str) -> str:
    return get_chat_response(message, thread_id)


def stream_chat_response(message: str, thread_id: str) -> Iterator[str]:
    return _stream_chat_response(message, thread_id)