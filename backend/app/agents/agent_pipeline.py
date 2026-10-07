# backend/app/agents/agent_pipeline.py

from app.agents.research_agent import run_research_agent
from app.agents.critic_agent import run_critic_agent
from app.logger.logger import logger

MAX_RETRIES = 3   # re-research if critic gives FAIL (up to 3 times)
PASS_THRESHOLD = 6.0  # lowered from 7 — avoids over-penalising factual answers


def run_agent_pipeline(query: str) -> dict:
    """
    Full Research → Critic pipeline.

    Flow:
        1. Research Agent  → produces a summary from web search.
        2. Critic Agent    → scores the summary.
        3. If FAIL + retries left → refine query and retry from step 1.
        4. Return final combined result.

    Args:
        query : user's research question

    Returns:
        dict with keys:
            - query          : original query
            - summary        : final research summary
            - critique       : critic's full evaluation dict
            - passed         : bool
            - attempts       : how many research attempts were made
    """

    attempt       = 0
    critic_result = None

    while attempt < MAX_RETRIES:
        attempt += 1
        logger.info(f"[pipeline] Attempt {attempt}/{MAX_RETRIES} for: '{query}'")

        # ── Step 1: Research ───────────────────────────────────────────────
        research_result = run_research_agent(query)

        # ── Step 2: Critic review ──────────────────────────────────────────
        critic_result = run_critic_agent(research_result)

        # Use our own threshold, not the critic's hardcoded 7.0
        passed = critic_result["critique"].get("overall_score", 0) >= PASS_THRESHOLD
        critic_result["passed"] = passed

        if passed:
            logger.info(f"[pipeline] PASSED on attempt {attempt}.")
            break

        logger.warning(
            f"[pipeline] FAILED (score={critic_result['critique'].get('overall_score')}) "
            f"— retrying with refined query..."
        )

        # ── Step 3: Refine query — keep it SHORT and specific ──────────────
        # Do NOT append full critic feedback — it bloats the Tavily search query
        # and causes irrelevant results on the retry.
        weakness = critic_result["critique"].get("weaknesses", [""])[0]
        if weakness:
            # Extract just the core issue in a few words, not the full sentence
            query = f"{research_result['query']} site:wikipedia.org OR site:whitehouse.gov OR site:reuters.com"
        else:
            query = research_result["query"]  # fallback: retry original query

    return {
        "query":    critic_result["query"],
        "summary":  critic_result["summary"],
        "critique": critic_result["critique"],
        "passed":   critic_result["passed"],
        "attempts": attempt,
    }