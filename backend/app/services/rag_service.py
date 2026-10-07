# backend/app/services/rag_service.py

from app.rag.rag_service import get_rag_response
from app.rag.rag_service import stream_rag_response as _stream_rag_response
from app.rag.rag_service import ingest_file
from typing import Iterator


def rag_response(query: str) -> dict:
    return get_rag_response(query)


def rag_stream_response(query: str) -> Iterator[str]:
    return _stream_rag_response(query)


def rag_ingest(file_path: str) -> dict:
    return ingest_file(file_path)