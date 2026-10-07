# backend/app/utils/helpers.py

import os
import re
import json
import uuid
import time
import hashlib
from pathlib import Path
from functools import wraps
from typing import Callable, Any

from app.logger.logger import logger


# ══════════════════════════════════════════════════════════════════════════════
# 1. ID HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def generate_thread_id() -> str:
    """Generate a new unique thread/session UUID string."""
    return str(uuid.uuid4())


def generate_file_id(file_path: str) -> str:
    """
    Generate a short deterministic ID for a file based on its path + size.
    Used to tag ingested document chunks with a stable source identifier.
    """
    stat   = os.stat(file_path)
    raw    = f"{file_path}:{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ══════════════════════════════════════════════════════════════════════════════
# 2. FILE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def validate_file_extension(filename: str) -> str:
    """
    Validate that an uploaded file has a supported extension.
    Returns the lowercased extension on success.
    Raises ValueError on unsupported type.

    Usage:
        ext = validate_file_extension("report.pdf")   # → ".pdf"
        ext = validate_file_extension("image.png")    # → raises ValueError
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    return ext


def get_file_size_mb(file_path: str) -> float:
    """Return file size in megabytes, rounded to 2 decimal places."""
    size_bytes = os.path.getsize(file_path)
    return round(size_bytes / (1024 * 1024), 2)


def ensure_dir(path: str) -> str:
    """Create a directory (and parents) if it doesn't exist. Returns the path."""
    os.makedirs(path, exist_ok=True)
    return path


def safe_filename(filename: str) -> str:
    """
    Sanitise an uploaded filename — strips path components and
    replaces spaces / special characters with underscores.

    Examples:
        "My Report (Final).pdf"  →  "My_Report__Final_.pdf"
        "../../../etc/passwd"    →  "passwd"
    """
    name = Path(filename).name          # strip any directory traversal
    name = re.sub(r"[^\w.\-]", "_", name)
    return name


# ══════════════════════════════════════════════════════════════════════════════
# 3. JSON / LLM OUTPUT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def parse_llm_json(text: str, fallback: dict | None = None) -> dict:
    """
    Safely parse a JSON string returned by an LLM.
    Strips markdown code fences (```json ... ```) if present.
    Returns `fallback` dict on parse failure instead of raising.

    Used by: critic_agent.py

    Args:
        text     : raw LLM response string
        fallback : dict to return when parsing fails (default: {})
    """
    if fallback is None:
        fallback = {}

    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"[helpers] JSON parse failed: {e} | raw: {cleaned[:200]}")
        return fallback


def truncate_text(text: str, max_chars: int = 400, suffix: str = "...") -> str:
    """
    Truncate a string to max_chars and append suffix if it was truncated.
    Used when formatting Tavily search snippets in research_agent.py.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + suffix


# ══════════════════════════════════════════════════════════════════════════════
# 4. TIMING / RETRY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def timeit(fn: Callable) -> Callable:
    """
    Decorator — logs how long a function takes to run.

    Usage:
        @timeit
        def run_rag_chain(query): ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs) -> Any:
        start  = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"[timeit] {fn.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Decorator factory — retries a function up to max_attempts times
    on the specified exception types, with a fixed delay between attempts.

    Usage:
        @retry(max_attempts=3, delay=2.0, exceptions=(ConnectionError,))
        def call_external_api(): ...
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    logger.warning(
                        f"[retry] {fn.__name__} attempt {attempt}/{max_attempts} "
                        f"failed: {e}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay)
            logger.error(f"[retry] {fn.__name__} exhausted all {max_attempts} attempts.")
            raise last_exc
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# 5. TEXT FORMATTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def format_sources(sources: list[str]) -> str:
    """
    Format a list of source file paths into a clean numbered string.

    Example:
        ["data/raw/report.pdf", "data/raw/notes.txt"]
        → "1. report.pdf\n2. notes.txt"
    """
    return "\n".join(
        f"{i}. {Path(s).name}" for i, s in enumerate(sources, start=1)
    )


def word_count(text: str) -> int:
    """Return approximate word count of a string."""
    return len(text.split())


def clean_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines into single spaces."""
    return re.sub(r"\s+", " ", text).strip()