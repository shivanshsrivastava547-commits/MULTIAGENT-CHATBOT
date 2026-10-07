# backend/app/agents/research_agent.py

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, SystemMessage
from app.config.settings import settings
from app.logger.logger import logger
from app.utils.helpers import truncate_text


# ── Tools ──────────────────────────────────────────────────────────────────
search_tool = TavilySearch(
    max_results=5,
    api_key=settings.TAVILY_API_KEY,
)

# ── LLM ───────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,          # lower temp → more factual research output
)

# ── System prompt ──────────────────────────────────────────────────────────
RESEARCH_SYSTEM_PROMPT = """You are an expert research assistant with access to real-time web search results.

CRITICAL RULES:
1. The web search results provided to you are LIVE data — they are MORE RECENT and MORE ACCURATE than your training data.
2. ALWAYS trust the web search results over your internal knowledge or training cutoff.
3. If the search results contain the answer, state it confidently and cite the source.
4. Do NOT say "my training data only goes up to X" — the search results override that limitation.
5. Only say information is unavailable if the search results genuinely contain no relevant data.

Your job is to:
1. Analyse the user's query carefully.
2. Use the web search results provided to you as your primary source of truth.
3. Synthesise a clear, factual, well-structured answer based on those results.
4. Always cite which search result supports each key point.
5. Be concise — no padding, no repetition.

Format your response as:
### Research Summary
<your synthesised answer here>

### Sources Used
<bullet list of URLs you relied on>
"""


# ── Main function ──────────────────────────────────────────────────────────
def run_research_agent(query: str) -> dict:
    """
    Research Agent entry point.

    Steps:
        1. Run Tavily web search for the query.
        2. Format search results into a context block.
        3. Ask Groq LLaMA to synthesise a clean answer.

    Args:
        query : The user's research question.

    Returns:
        dict with keys:
            - query          : original query
            - search_results : raw list from Tavily
            - summary        : LLM-synthesised answer string
    """

    logger.info(f"[research_agent] Starting research for: '{query}'")

    # ── Step 1: Web search ─────────────────────────────────────────────────
    try:
        raw = search_tool.invoke(query)

        # langchain-tavily 0.2.x returns the full Tavily API response as a dict:
        # { "query": ..., "answer": ..., "results": [...], "images": [...], ... }
        # The actual search hits are nested inside "results".
        tavily_direct_answer = ""
        if isinstance(raw, dict):
            tavily_direct_answer = raw.get("answer", "") or ""
            search_results = raw.get("results", [])
        elif isinstance(raw, list):
            search_results = raw
        else:
            search_results = []

        logger.info(f"[research_agent] Got {len(search_results)} results.")
    except Exception as e:
        logger.error(f"[research_agent] Search error: {e}")
        raise

    # ── Step 2: Format results as readable context ─────────────────────────
    context_block = _format_results(search_results)

    # Prepend Tavily's own direct answer if available — it's highly accurate
    if tavily_direct_answer:
        context_block = f"[Tavily Direct Answer]: {tavily_direct_answer}\n\n" + context_block

    # ── Step 3: LLM synthesis ──────────────────────────────────────────────
    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Query: {query}\n\n"
            f"Web Search Results:\n{context_block}\n\n"
            "Now write your research summary."
        )),
    ]

    try:
        response = llm.invoke(messages)
        summary: str = response.content
        logger.info("[research_agent] Summary generated successfully.")
    except Exception as e:
        logger.error(f"[research_agent] LLM error: {e}")
        raise

    return {
        "query":          query,
        "search_results": search_results,
        "summary":        summary,
    }


# ── Helper ─────────────────────────────────────────────────────────────────
def _format_results(results: list) -> str:
    """
    Convert Tavily result dicts OR strings into a numbered, readable string block.

    In langchain-tavily >= 0.2, results may be list[str] or list[dict].
    """
    lines = []
    for i, r in enumerate(results, start=1):
        if isinstance(r, dict):
            title   = r.get("title",   "No title")
            url     = r.get("url",     "No URL")
            content = r.get("content", "").strip()
            lines.append(
                f"[{i}] {title}\n"
                f"     URL: {url}\n"
                f"     Snippet: {truncate_text(content, max_chars=400)}"
            )
        elif isinstance(r, str):
            lines.append(f"[{i}] {truncate_text(r, max_chars=400)}")
        else:
            lines.append(f"[{i}] {truncate_text(str(r), max_chars=400)}")
    return "\n\n".join(lines)