import os

# =========================
# Helper Function
# =========================
def create_file(path: str, content: str = ""):
    """
    Creates a file with given content.
    Ensures directory exists before creating file.
    """
    dir_name = os.path.dirname(path)

    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# =========================
# File Definitions
# =========================
files = {

# ---------------- BACKEND ----------------
"backend/app/main.py": """from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI Chatbot with RAG")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}
""",

"backend/app/config/settings.py": """class Settings:
    PROJECT_NAME = "AI Chatbot"
    VERSION = "1.0.0"

settings = Settings()
""",

"backend/app/logger/logger.py": """import logging
import os

LOG_DIR = "backend/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
""",

"backend/app/database/sqlite_db.py": """import sqlite3

def get_connection():
    return sqlite3.connect("chat.db")
""",

"backend/app/chatbot/graph.py": "# LangGraph logic here\n",
"backend/app/chatbot/nodes.py": "# Nodes here\n",
"backend/app/chatbot/service.py": """def get_chat_response(message: str):
    return f"Echo: {message}"
""",

"backend/app/rag/ingest.py": "# RAG ingestion logic\n",
"backend/app/rag/retriever.py": "# Retriever logic\n",
"backend/app/rag/rag_chain.py": "# RAG chain logic\n",
"backend/app/rag/service.py": """def get_rag_response(query: str):
    return f"RAG Answer: {query}"
""",

"backend/app/agents/research_agent.py": "# Research agent\n",
"backend/app/agents/critic_agent.py": "# Critic agent\n",

"backend/app/api/routes.py": """from fastapi import APIRouter
from app.services.chat_service import chat_response
from app.services.rag_service import rag_response

router = APIRouter()

@router.post("/chat")
def chat(data: dict):
    return {"response": chat_response(data["message"])}

@router.post("/rag")
def rag(data: dict):
    return {"response": rag_response(data["query"])}
""",

"backend/app/api/schemas.py": """from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class RAGRequest(BaseModel):
    query: str
""",

"backend/app/utils/helpers.py": "# Utility functions\n",

"backend/app/services/chat_service.py": """from app.chatbot.service import get_chat_response

def chat_response(message: str):
    return get_chat_response(message)
""",

"backend/app/services/rag_service.py": """from app.rag.service import get_rag_response

def rag_response(query: str):
    return get_rag_response(query)
""",

"backend/requirements.txt": """fastapi
uvicorn
pydantic
langchain
langgraph
faiss-cpu
python-dotenv
sqlite3
""",

"backend/Dockerfile": """FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

"backend/.env": "OPENAI_API_KEY=your_key_here\n",


# ---------------- FRONTEND ----------------
"frontend/public/index.html": """<!DOCTYPE html>
<html>
<head>
  <title>AI Chat</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
""",

"frontend/src/main.jsx": """import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",

"frontend/src/App.jsx": """import Chat from "./pages/Chat";

function App() {
  return <Chat />;
}

export default App;
""",

"frontend/src/pages/Chat.jsx": """import { useState } from "react";
import { sendMessage } from "../services/api";

export default function Chat() {
  const [msg, setMsg] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    const res = await sendMessage(msg);
    setResponse(res.response);
  };

  return (
    <div>
      <h1>Chat UI</h1>
      <input value={msg} onChange={(e) => setMsg(e.target.value)} />
      <button onClick={handleSend}>Send</button>
      <p>{response}</p>
    </div>
  );
}
""",

"frontend/src/services/api.js": """import axios from "axios";

const API = "http://localhost:8000";

export const sendMessage = async (message) => {
  const res = await axios.post(`${API}/chat`, { message });
  return res.data;
};
""",

"frontend/package.json": """{
  "name": "frontend",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^1.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "scripts": {
    "start": "vite"
  }
}
""",


# ---------------- ROOT ----------------
"docker-compose.yml": """version: "3"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    image: node:18
    working_dir: /app
    volumes:
      - ./frontend:/app
    command: npm install && npm run start
    ports:
      - "3000:3000"
""",

"README.md": "# AI Chatbot with RAG 🚀\n",

".gitignore": """__pycache__/
*.pyc
venv/
.env
node_modules/
logs/
"""
}


# =========================
# Create Files
# =========================
for path, content in files.items():
    create_file(path, content)


# =========================
# Create Folders
# =========================
folders = [
    "backend/app/chatbot",
    "backend/app/rag",
    "backend/app/agents",
    "backend/app/api",
    "backend/app/utils",
    "backend/app/services",
    "backend/app/config",
    "backend/app/logger",
    "backend/app/database",
    "backend/logs",
    "backend/tests",
    "frontend/src/components",
    "frontend/src/hooks",
    "frontend/src/context",
    "frontend/src/styles",
    "frontend/src/assets",
    "vectorstore",
    "data/raw",
    "data/processed",
    "notebooks"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)


print("✅ Project structure created successfully!")