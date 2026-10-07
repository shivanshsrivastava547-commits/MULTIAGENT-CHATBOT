# backend/app/config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "AI Chatbot with RAG"
    VERSION: str      = "1.0.0"

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str   = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    # SQLite — global shared DB for all features
    # Default to /app/data/chatbot.db (absolute path, created by Dockerfile).
    # Override via SQLITE_DB_PATH env var in Render/docker-compose if needed.
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "/app/data/chatbot.db")

    # Pinecone (replaces FAISS)
    PINECONE_API_KEY:    str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "rag-index")

    # Embeddings (local, free — HuggingFace)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    RAG_TOP_K:       int = int(os.getenv("RAG_TOP_K", "4"))

    # Tavily (web search for agents)
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")


settings = Settings()
