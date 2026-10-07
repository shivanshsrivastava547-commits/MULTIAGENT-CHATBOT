# backend/app/logger/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

# ── Config ─────────────────────────────────────────────────────────────────
# Use LOG_DIR env var if set; otherwise default to /app/logs (absolute path).
# NOTE: The old "../../../logs" relative path resolved to the filesystem root
#       inside Docker (/app/app/logger/../../../logs → /logs) causing a
#       PermissionError. Always use an absolute path in containers.
LOG_DIR  = os.environ.get("LOG_DIR", os.path.join("/app", "logs"))
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

# ── Format ─────────────────────────────────────────────────────────────────
LOG_FORMAT  = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ── Logger factory ─────────────────────────────────────────────────────────
def get_logger(name: str = "app") -> logging.Logger:
    """
    Returns a named logger with:
      - Console handler  (INFO+)   — visible in terminal / Docker logs
      - File handler     (DEBUG+)  — rotating, max 5MB × 3 backups
    
    Usage:
        from app.logger.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Server started")
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured — avoid duplicate handlers on re-import
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── Console handler ────────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ── Rotating file handler ──────────────────────────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB per file
        backupCount=3,               # keep app.log, app.log.1, app.log.2
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# ── Default app logger (used across all modules) ───────────────────────────
logger = get_logger("app")