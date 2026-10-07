# backend/app/api/routes.py

import json
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from app.api.schemas import (
    ChatRequest, ChatResponse,
    RAGRequest,
    ResearchRequest, ResearchResponse,
)
from app.services.chat_service import chat_response, stream_chat_response
from app.services.rag_service import rag_response, rag_stream_response, rag_ingest as rag_ingest_file
from app.agents.agent_pipeline import run_agent_pipeline
from app.chatbot.graph import retrieve_all_threads
from app.logger.logger import logger

router = APIRouter()


# ── Chat: standard invoke ──────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):
    try:
        reply = chat_response(data.message, data.thread_id)
        return ChatResponse(response=reply, thread_id=data.thread_id)
    except Exception as e:
        logger.error(f"[routes] /chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Chat: streaming (SSE) ──────────────────────────────────────────────────
@router.post("/chat/stream")
def chat_stream(data: ChatRequest):
    """
    Server-Sent Events endpoint — streams tokens as they arrive from Groq.
    React frontend consumes this with EventSource or fetch + ReadableStream.

    Each chunk is sent as:   data: <token_text>\\n\\n
    Final chunk is:          data: [DONE]\\n\\n
    """
    def event_generator():
        try:
            for chunk in stream_chat_response(data.message, data.thread_id):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"[routes] /chat/stream error: {e}")
            yield f"data: [ERROR] {json.dumps(str(e))}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",      # disables Nginx buffering
        },
    )


# ── Threads list ───────────────────────────────────────────────────────────
@router.get("/threads")
def get_threads():
    """Returns all thread_ids stored in the SqliteSaver checkpointer."""
    return {"threads": retrieve_all_threads()}


# ── RAG: ask a question ────────────────────────────────────────────────────
@router.post("/rag")
def rag(data: RAGRequest):
    """
    Ask a question against ingested documents.
    Returns answer + list of source files used.
    """
    try:
        result = rag_response(data.query)
        return {"answer": result["answer"], "sources": result["sources"], "thread_id": data.thread_id}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[routes] /rag error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── RAG: streaming ─────────────────────────────────────────────────────────
@router.post("/rag/stream")
def rag_stream(data: RAGRequest):
    """Stream RAG answer token-by-token via SSE."""
    def event_generator():
        try:
            for chunk in rag_stream_response(data.query):
                yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except FileNotFoundError as e:
            yield f"data: [ERROR] {json.dumps(str(e))}\n\n"
        except Exception as e:
            logger.error(f"[routes] /rag/stream error: {e}")
            yield f"data: [ERROR] {json.dumps(str(e))}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── RAG: ingest a document ─────────────────────────────────────────────────
@router.post("/rag/ingest")
async def rag_ingest(file: UploadFile = File(...)):
    """
    Upload and ingest a document (PDF / TXT / DOCX) into the FAISS vectorstore.
    """
    import shutil
    from pathlib import Path
    from app.utils.helpers import safe_filename, validate_file_extension, ensure_dir

    try:
        validate_file_extension(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    RAW_DIR   = ensure_dir("data/raw")
    filename  = safe_filename(file.filename)
    file_path = str(Path(RAW_DIR) / filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(f"[routes] /rag/ingest — saved {filename}")

    try:
        result = rag_ingest_file(file_path)
        return result
    except Exception as e:
        logger.error(f"[routes] /rag/ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Research + Critic endpoint ─────────────────────────────────────────────
@router.post("/research", response_model=ResearchResponse)
def research(data: ResearchRequest):
    try:
        result = run_agent_pipeline(data.query)
        return ResearchResponse(**result)
    except Exception as e:
        logger.error(f"[routes] /research error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
