# backend/app/main.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.sqlite_db import init_db
from app.logger.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising global SQLite DB...")
    init_db()
    yield
    logger.info("Shutting down.")


app = FastAPI(title="AI Chatbot with RAG", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # ALLOWED_ORIGINS env var: comma-separated list of allowed origins.
    # e.g. "https://my-frontend.onrender.com,http://localhost:5173"
    allow_origins=[
        o.strip()
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000",
        ).split(",")
        if o.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def home():
    return {"message": "Backend is running"}
