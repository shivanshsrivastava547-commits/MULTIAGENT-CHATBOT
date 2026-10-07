# ══════════════════════════════════════════════════════════════════════════════
# Stage 1 — dependency builder
# ══════════════════════════════════════════════════════════════════════════════
FROM python:3.10-slim AS builder

WORKDIR /app

# System deps for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements first — Docker caches this layer
COPY requirements.txt .

# Install all packages
# NOTE: No torch/sentence-transformers anymore — we use fastembed (ONNX-based).
# fastembed is ~50MB and has NO CUDA/GPU dependencies, making it safe for
# Render's free tier (512MB RAM).
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ══════════════════════════════════════════════════════════════════════════════
# Stage 2 — final runtime image (slim, no build tools)
# ══════════════════════════════════════════════════════════════════════════════
FROM python:3.10-slim AS runtime

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY --chown=appuser:appuser . .

# Create writable directories and fix ownership of /app
# WORKDIR creates /app as root — appuser needs write access for chatbot.db etc.
RUN mkdir -p logs vectorstore data/raw data/processed && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# ── Environment defaults ─────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Expose port
EXPOSE 8000

# ── Start command ──────────────────────────────────────────────────────────
# Render injects $PORT — shell form allows ${PORT:-8000} variable expansion.
CMD exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info