# backend/app/api/schemas.py

from pydantic import BaseModel, Field
import uuid


def _new_thread() -> str:
    return str(uuid.uuid4())


# ── Chat schemas ───────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message:   str = Field(..., min_length=1, description="User message")
    thread_id: str = Field(default_factory=_new_thread,
                           description="Conversation thread ID (uuid)")


class ChatResponse(BaseModel):
    response:  str
    thread_id: str


# ── RAG schemas ────────────────────────────────────────────────────────────
class RAGRequest(BaseModel):
    query:     str = Field(..., min_length=1)
    thread_id: str = Field(default_factory=_new_thread)


class RAGResponse(BaseModel):
    response:  str
    thread_id: str


# ── Research / Critic schemas ──────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Research question")


class CritiqueScores(BaseModel):
    accuracy:     int
    completeness: int
    clarity:      int
    source_usage: int


class CritiqueDetail(BaseModel):
    scores:        CritiqueScores
    overall_score: float
    verdict:       str
    strengths:     list[str]
    weaknesses:    list[str]
    feedback:      str


class ResearchResponse(BaseModel):
    query:    str
    summary:  str
    critique: CritiqueDetail
    passed:   bool
    attempts: int
