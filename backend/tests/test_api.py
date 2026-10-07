# backend/tests/test_api.py

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ══════════════════════════════════════════════════════════════════════════════
# /api/chat
# ══════════════════════════════════════════════════════════════════════════════

class TestChatEndpoint:

    @patch("app.api.routes.chat_response", return_value="Hello from mock!")
    def test_chat_returns_200(self, _):
        response = client.post("/api/chat", json={
            "message":   "Hello",
            "thread_id": "test-thread-001",
        })
        assert response.status_code == 200

    @patch("app.api.routes.chat_response", return_value="Hello from mock!")
    def test_chat_response_body(self, _):
        response = client.post("/api/chat", json={
            "message":   "Hello",
            "thread_id": "test-thread-001",
        })
        data = response.json()
        assert data["response"]  == "Hello from mock!"
        assert data["thread_id"] == "test-thread-001"

    def test_chat_missing_message_returns_422(self):
        response = client.post("/api/chat", json={"thread_id": "t1"})
        assert response.status_code == 422

    def test_chat_empty_message_returns_422(self):
        response = client.post("/api/chat", json={"message": "", "thread_id": "t1"})
        assert response.status_code == 422

    @patch("app.api.routes.chat_response", side_effect=Exception("LLM error"))
    def test_chat_llm_error_returns_500(self, _):
        response = client.post("/api/chat", json={
            "message":   "Hello",
            "thread_id": "test-thread-001",
        })
        assert response.status_code == 500


# ══════════════════════════════════════════════════════════════════════════════
# /api/rag
# ══════════════════════════════════════════════════════════════════════════════

class TestRagEndpoint:

    @patch("app.api.routes.rag_response", return_value={
        "answer":  "LangGraph is a framework.",
        "sources": ["doc.pdf"],
    })
    def test_rag_returns_200(self, _):
        response = client.post("/api/rag", json={
            "query":     "What is LangGraph?",
            "thread_id": "test-thread-002",
        })
        assert response.status_code == 200

    @patch("app.api.routes.rag_response", return_value={
        "answer":  "LangGraph is a framework.",
        "sources": ["doc.pdf"],
    })
    def test_rag_response_body(self, _):
        response = client.post("/api/rag", json={
            "query":     "What is LangGraph?",
            "thread_id": "test-thread-002",
        })
        data = response.json()
        assert "answer"  in data
        assert "sources" in data

    @patch("app.api.routes.rag_response", side_effect=FileNotFoundError("No index"))
    def test_rag_no_index_returns_404(self, _):
        response = client.post("/api/rag", json={
            "query":     "anything",
            "thread_id": "t1",
        })
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
# /api/threads
# ══════════════════════════════════════════════════════════════════════════════

class TestThreadsEndpoint:

    @patch("app.api.routes.retrieve_all_threads", return_value=["t1", "t2", "t3"])
    def test_threads_returns_list(self, _):
        response = client.get("/api/threads")
        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert len(data["threads"]) == 3


# ══════════════════════════════════════════════════════════════════════════════
# /api/research
# ══════════════════════════════════════════════════════════════════════════════

class TestResearchEndpoint:

    @patch("app.api.routes.run_agent_pipeline", return_value={
        "query":    "What is LangGraph?",
        "summary":  "LangGraph is a framework.",
        "critique": {
            "scores":        {"accuracy": 8, "completeness": 8, "clarity": 9, "source_usage": 8},
            "overall_score": 8.3,
            "verdict":       "PASS",
            "strengths":     ["Clear"],
            "weaknesses":    [],
            "feedback":      "Good job.",
        },
        "passed":   True,
        "attempts": 1,
    })
    def test_research_returns_200(self, _):
        response = client.post("/api/research", json={"query": "What is LangGraph?"})
        assert response.status_code == 200

    @patch("app.api.routes.run_agent_pipeline", side_effect=Exception("Agent failed"))
    def test_research_error_returns_500(self, _):
        response = client.post("/api/research", json={"query": "test"})
        assert response.status_code == 500


# ══════════════════════════════════════════════════════════════════════════════
# health check
# ══════════════════════════════════════════════════════════════════════════════

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()