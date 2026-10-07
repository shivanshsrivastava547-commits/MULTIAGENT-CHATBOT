# backend/app/chatbot/nodes.py

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from app.chatbot.state import ChatState
from app.config.settings import settings
from app.logger.logger import logger


# ── LLM ───────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.7,
)


# ── chat_node ──────────────────────────────────────────────────────────────
def chat_node(state: ChatState) -> dict:
    """
    Single node — receives full message history from checkpointer,
    prepends a system prompt, calls Groq LLaMA, returns AI reply.
    SqliteSaver automatically persists state after this node completes.
    """

    logger.info(f"[chat_node] messages in state: {len(state['messages'])}")

    messages_to_send = [
        SystemMessage(content="You are a helpful AI assistant."),
        *state["messages"],
    ]

    try:
        response = llm.invoke(messages_to_send)
        logger.info("[chat_node] LLM responded successfully.")
    except Exception as e:
        logger.error(f"[chat_node] LLM error: {e}")
        raise

    return {"messages": [response]}
