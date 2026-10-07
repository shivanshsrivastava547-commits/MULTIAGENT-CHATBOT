# backend/tests/conftest.py

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage


# ── Shared fixtures ────────────────────────────────────────────────────────

@pytest.fixture
def sample_thread_id():
    return "test-thread-1234"


@pytest.fixture
def sample_human_message():
    return HumanMessage(content="Hello, how are you?")


@pytest.fixture
def sample_ai_message():
    return AIMessage(content="I am doing well, thank you!")


@pytest.fixture
def sample_chat_state(sample_human_message, sample_ai_message):
    return {
        "messages": [sample_human_message, sample_ai_message],
    }


@pytest.fixture
def mock_llm_response():
    """Mock a Groq LLM response object."""
    mock = MagicMock()
    mock.content = "This is a mock AI response."
    return mock


@pytest.fixture
def sample_research_output():
    return {
        "query": "What is LangGraph?",
        "search_results": [
            {"url": "https://example.com/1", "title": "LangGraph Intro", "content": "LangGraph is a framework..."},
            {"url": "https://example.com/2", "title": "LangGraph Docs",  "content": "It supports stateful agents..."},
        ],
        "summary": "### Research Summary\nLangGraph is a framework for building stateful LLM agents.\n\n### Sources Used\n- https://example.com/1",
    }