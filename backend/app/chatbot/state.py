# backend/app/chatbot/state.py

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """
    Minimal state — messages only.
    LangGraph's SqliteSaver checkpointer handles
    full history persistence automatically via thread_id in config.
    """
    messages: Annotated[list[BaseMessage], add_messages]
