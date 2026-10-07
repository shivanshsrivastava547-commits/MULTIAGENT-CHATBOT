# backend/tests/test_agents.py

import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════════════════════════════
# test research_agent
# ══════════════════════════════════════════════════════════════════════════════

class TestResearchAgent:

    @patch("app.agents.research_agent.llm")
    @patch("app.agents.research_agent.search_tool")
    def test_run_research_agent_returns_expected_keys(self, mock_search, mock_llm):
        from app.agents.research_agent import run_research_agent

        mock_search.invoke.return_value = [
            {"url": "https://example.com", "title": "Test", "content": "Some content here."}
        ]
        mock_response         = MagicMock()
        mock_response.content = "### Research Summary\nLangGraph is a framework."
        mock_llm.invoke.return_value = mock_response

        result = run_research_agent("What is LangGraph?")

        assert "query"          in result
        assert "summary"        in result
        assert "search_results" in result

    @patch("app.agents.research_agent.llm")
    @patch("app.agents.research_agent.search_tool")
    def test_run_research_agent_passes_query(self, mock_search, mock_llm):
        from app.agents.research_agent import run_research_agent

        mock_search.invoke.return_value = []
        mock_llm.invoke.return_value    = MagicMock(content="summary")

        result = run_research_agent("test query")
        assert result["query"] == "test query"

    @patch("app.agents.research_agent.search_tool")
    def test_run_research_agent_raises_on_search_error(self, mock_search):
        from app.agents.research_agent import run_research_agent

        mock_search.invoke.side_effect = ConnectionError("Tavily down")

        with pytest.raises(ConnectionError):
            run_research_agent("query")

    def test_format_results_basic(self):
        from app.agents.research_agent import _format_results

        results = [
            {"title": "Test Title", "url": "https://example.com", "content": "Some content."}
        ]
        output = _format_results(results)

        assert "[1]" in output
        assert "Test Title" in output
        assert "https://example.com" in output


# ══════════════════════════════════════════════════════════════════════════════
# test critic_agent
# ══════════════════════════════════════════════════════════════════════════════

class TestCriticAgent:

    @patch("app.agents.critic_agent.llm")
    def test_run_critic_agent_pass_verdict(self, mock_llm, sample_research_output):
        from app.agents.critic_agent import run_critic_agent

        mock_response         = MagicMock()
        mock_response.content = """{
            "scores": {"accuracy": 8, "completeness": 8, "clarity": 9, "source_usage": 8},
            "overall_score": 8.3,
            "verdict": "PASS",
            "strengths": ["Clear writing"],
            "weaknesses": ["Could cite more"],
            "feedback": "Add more citations."
        }"""
        mock_llm.invoke.return_value = mock_response

        result = run_critic_agent(sample_research_output)

        assert result["passed"]                     is True
        assert result["critique"]["verdict"]         == "PASS"
        assert result["critique"]["overall_score"]   == 8.3

    @patch("app.agents.critic_agent.llm")
    def test_run_critic_agent_fail_verdict(self, mock_llm, sample_research_output):
        from app.agents.critic_agent import run_critic_agent

        mock_response         = MagicMock()
        mock_response.content = """{
            "scores": {"accuracy": 4, "completeness": 5, "clarity": 6, "source_usage": 4},
            "overall_score": 4.8,
            "verdict": "FAIL",
            "strengths": [],
            "weaknesses": ["Too vague"],
            "feedback": "Needs more detail."
        }"""
        mock_llm.invoke.return_value = mock_response

        result = run_critic_agent(sample_research_output)

        assert result["passed"]                   is False
        assert result["critique"]["verdict"]       == "FAIL"

    @patch("app.agents.critic_agent.llm")
    def test_run_critic_agent_handles_bad_json(self, mock_llm, sample_research_output):
        from app.agents.critic_agent import run_critic_agent

        mock_response         = MagicMock()
        mock_response.content = "not valid json at all"
        mock_llm.invoke.return_value = mock_response

        # Should NOT raise — parse_llm_json returns fallback
        result = run_critic_agent(sample_research_output)
        assert result["critique"]["verdict"] == "PARSE_ERROR"
        assert result["passed"] is False


# ══════════════════════════════════════════════════════════════════════════════
# test agent_pipeline
# ══════════════════════════════════════════════════════════════════════════════

class TestAgentPipeline:

    @patch("app.agents.agent_pipeline.run_critic_agent")
    @patch("app.agents.agent_pipeline.run_research_agent")
    def test_pipeline_passes_on_first_attempt(self, mock_research, mock_critic):
        from app.agents.agent_pipeline import run_agent_pipeline

        mock_research.return_value = {"query": "q", "search_results": [], "summary": "s"}
        mock_critic.return_value   = {
            "query": "q", "summary": "s",
            "critique": {"overall_score": 8.0, "verdict": "PASS",
                         "scores": {}, "strengths": [], "weaknesses": [], "feedback": ""},
            "passed": True,
        }

        result = run_agent_pipeline("What is LangGraph?")

        assert result["passed"]   is True
        assert result["attempts"] == 1
        mock_research.assert_called_once()

    @patch("app.agents.agent_pipeline.run_critic_agent")
    @patch("app.agents.agent_pipeline.run_research_agent")
    def test_pipeline_retries_on_fail(self, mock_research, mock_critic):
        from app.agents.agent_pipeline import run_agent_pipeline

        mock_research.return_value = {"query": "q", "search_results": [], "summary": "s"}

        fail_result = {
            "query": "q", "summary": "s",
            "critique": {"overall_score": 4.0, "verdict": "FAIL",
                         "scores": {}, "strengths": [], "weaknesses": [],
                         "feedback": "needs more detail"},
            "passed": False,
        }
        pass_result = {
            "query": "q", "summary": "s improved",
            "critique": {"overall_score": 8.5, "verdict": "PASS",
                         "scores": {}, "strengths": [], "weaknesses": [], "feedback": ""},
            "passed": True,
        }
        mock_critic.side_effect = [fail_result, pass_result]

        result = run_agent_pipeline("What is LangGraph?")

        assert result["passed"]   is True
        assert result["attempts"] == 2
        assert mock_research.call_count == 2