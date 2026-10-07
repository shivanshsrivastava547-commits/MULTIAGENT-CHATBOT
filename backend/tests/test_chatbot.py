# backend/tests/test_chatbot.py

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ══════════════════════════════════════════════════════════════════════════════
# test chat_node
# ══════════════════════════════════════════════════════════════════════════════

class TestChatNode:

    @patch("app.chatbot.nodes.llm")
    def test_chat_node_returns_ai_message(self, mock_llm, sample_chat_state, mock_llm_response):
        from app.chatbot.nodes import chat_node

        mock_llm.invoke.return_value = mock_llm_response

        result = chat_node(sample_chat_state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "This is a mock AI response."

    @patch("app.chatbot.nodes.llm")
    def test_chat_node_prepends_system_message(self, mock_llm, sample_chat_state, mock_llm_response):
        from app.chatbot.nodes import chat_node

        mock_llm.invoke.return_value = mock_llm_response
        chat_node(sample_chat_state)

        call_args = mock_llm.invoke.call_args[0][0]   # first positional arg = messages list
        assert isinstance(call_args[0], SystemMessage)

    @patch("app.chatbot.nodes.llm")
    def test_chat_node_raises_on_llm_error(self, mock_llm, sample_chat_state):
        from app.chatbot.nodes import chat_node

        mock_llm.invoke.side_effect = ConnectionError("Groq API down")

        with pytest.raises(ConnectionError):
            chat_node(sample_chat_state)

    @patch("app.chatbot.nodes.llm")
    def test_chat_node_includes_all_history(self, mock_llm, mock_llm_response):
        from app.chatbot.nodes import chat_node

        mock_llm.invoke.return_value = mock_llm_response

        state = {
            "messages": [
                HumanMessage(content="First message"),
                AIMessage(content="First reply"),
                HumanMessage(content="Second message"),
            ]
        }

        chat_node(state)

        call_args = mock_llm.invoke.call_args[0][0]
        # SystemMessage + 3 history messages = 4 total
        assert len(call_args) == 4


# ══════════════════════════════════════════════════════════════════════════════
# test get_chat_response (service)
# ══════════════════════════════════════════════════════════════════════════════

class TestChatService:

    @patch("app.chatbot.service.chatbot")
    def test_get_chat_response_returns_string(self, mock_chatbot, sample_thread_id):
        from app.chatbot.service import get_chat_response

        mock_chatbot.invoke.return_value = {
            "messages": [AIMessage(content="Hello from mock!")]
        }

        result = get_chat_response("Hi there", sample_thread_id)

        assert isinstance(result, str)
        assert result == "Hello from mock!"

    @patch("app.chatbot.service.chatbot")
    def test_get_chat_response_passes_thread_id_in_config(self, mock_chatbot, sample_thread_id):
        from app.chatbot.service import get_chat_response

        mock_chatbot.invoke.return_value = {
            "messages": [AIMessage(content="reply")]
        }

        get_chat_response("test message", sample_thread_id)

        call_kwargs = mock_chatbot.invoke.call_args
        config      = call_kwargs[1]["config"]   # keyword arg

        assert config["configurable"]["thread_id"] == sample_thread_id

    @patch("app.chatbot.service.chatbot")
    def test_stream_chat_response_yields_chunks(self, mock_chatbot, sample_thread_id):
        from app.chatbot.service import stream_chat_response

        chunk1  = MagicMock(); chunk1.content = "Hello "
        chunk2  = MagicMock(); chunk2.content = "world"
        mock_chatbot.stream.return_value = [
            (chunk1, {}),
            (chunk2, {}),
        ]

        chunks = list(stream_chat_response("Hi", sample_thread_id))
        assert chunks == ["Hello ", "world"]