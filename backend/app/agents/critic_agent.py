# backend/app/agents/critic_agent.py

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.config.settings import settings
from app.logger.logger import logger
from app.utils.helpers import parse_llm_json


# ── LLM ───────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.1,          # very low temp → consistent, structured scores
)

# ── System prompt ──────────────────────────────────────────────────────────
CRITIC_SYSTEM_PROMPT = """You are a strict but fair research quality critic.
Your job is to evaluate a research summary written by an AI research assistant.

Score the summary on these 4 criteria (each out of 10):
1. Accuracy       — Is the information factually correct based on the sources?
2. Completeness   — Does it fully answer the original query?
3. Clarity        — Is it well-written and easy to understand?
4. Source Usage   — Does it properly reference the search results provided?

Then compute an Overall Score (average of the 4 scores, out of 10).

Respond ONLY in this exact JSON format (no extra text):
{
  "scores": {
    "accuracy":       <int 1-10>,
    "completeness":   <int 1-10>,
    "clarity":        <int 1-10>,
    "source_usage":   <int 1-10>
  },
  "overall_score":  <float, 1 decimal place>,
  "verdict":        "<PASS if overall >= 7, FAIL if overall < 7>",
  "strengths":      ["<strength 1>", "<strength 2>"],
  "weaknesses":     ["<weakness 1>", "<weakness 2>"],
  "feedback":       "<1-2 sentence actionable improvement suggestion>"
}
"""


# ── Main function ──────────────────────────────────────────────────────────
def run_critic_agent(research_output: dict) -> dict:
    """
    Critic Agent entry point.

    Reviews the output from run_research_agent() and returns a structured
    quality report.

    Args:
        research_output : dict returned by run_research_agent(), with keys:
                            - query
                            - search_results
                            - summary

    Returns:
        dict with keys:
            - query          : original query
            - summary        : the research summary that was reviewed
            - critique       : full parsed critique dict (scores, verdict, etc.)
            - passed         : bool — True if overall_score >= 7
    """

    query   = research_output.get("query",   "")
    summary = research_output.get("summary", "")
    sources = research_output.get("search_results", [])

    logger.info(f"[critic_agent] Reviewing research for: '{query}'")

    # ── Build source reference string ─────────────────────────────────────
    source_refs = "\n".join(
        f"  [{i+1}] {r.get('url', 'N/A') if isinstance(r, dict) else str(r)[:200]}"
        for i, r in enumerate(sources)
    )

    # ── Ask LLM to critique ───────────────────────────────────────────────
    messages = [
        SystemMessage(content=CRITIC_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Original Query:\n{query}\n\n"
            f"Sources Available:\n{source_refs}\n\n"
            f"Research Summary to Review:\n{summary}\n\n"
            "Provide your critique in the required JSON format."
        )),
    ]

    try:
        response  = llm.invoke(messages)
        raw_text  = response.content.strip()
        fallback  = {
            "scores": {"accuracy": 0, "completeness": 0, "clarity": 0, "source_usage": 0},
            "overall_score": 0.0,
            "verdict":       "PARSE_ERROR",
            "strengths":     [],
            "weaknesses":    ["Could not parse critic response."],
            "feedback":      "Raw LLM output could not be parsed as JSON.",
        }
        critique  = parse_llm_json(raw_text, fallback=fallback)
        logger.info(f"[critic_agent] Verdict: {critique.get('verdict')} | "
                    f"Score: {critique.get('overall_score')}")
    except Exception as e:
        logger.error(f"[critic_agent] Error: {e}")
        raise

    passed = critique.get("overall_score", 0) >= 7.0

    return {
        "query":    query,
        "summary":  summary,
        "critique": critique,
        "passed":   passed,
    }