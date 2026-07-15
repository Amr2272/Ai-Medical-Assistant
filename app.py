"""
=========================================================
AI Medical Assistant
FastAPI Backend
=========================================================
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

# =========================================================
# Import AI System
# =========================================================

from src.rag import RAGOrchestrator
from src.config import (
    DATA_DIR,
    DEVICE,
)

# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("MedicalAI")

# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

TEMPLATE_DIR = BASE_DIR / "templates"

UPLOAD_DIR = Path(DATA_DIR)

UPLOAD_DIR.mkdir(exist_ok=True)

CHAT_HISTORY_FILE = UPLOAD_DIR / "chat_history.json"

# =========================================================
# Globals
# =========================================================

rag_system = None

load_error = None

# =========================================================
# Lifespan
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_system, load_error

    try:
        rag_system = RAGOrchestrator.from_data_directory()
        logger.info("Knowledge Base Loaded Successfully")
        
        # Pre-load existing chat history into RAG system
        with _history_lock:
            for session_id, session_data in history.items():
                if "messages" in session_data:
                    history_obj = rag_system._get_session_history(session_id)
                    # Clear existing in-memory history to avoid duplicates
                    history_obj.clear()
                    for msg in session_data["messages"]:
                        if msg["role"] == "user":
                            history_obj.add_user_message(msg["content"])
                        else:
                            history_obj.add_ai_message(msg["content"])
        logger.info("Chat history pre-loaded into RAG system")

    except Exception as e:
        logger.exception(e)
        load_error = str(e)

    yield

# =========================================================
# FastAPI
# =========================================================

app = FastAPI(

    title="AI Medical Assistant",

    version="2.0.0",

    lifespan=lifespan

)

# =========================================================
# Middleware
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)

# =========================================================
# Static
# =========================================================

app.mount(

    "/static",

    StaticFiles(directory=STATIC_DIR),

    name="static"

)

templates = Jinja2Templates(

    directory=TEMPLATE_DIR

)

# =========================================================
# Pydantic Models
# =========================================================

class ChatRequest(BaseModel):

    message: str

    session_id: str | None = None

    user_id: str


class RenameChatRequest(BaseModel):

    session_id: str

    title: str


class SessionInfo(BaseModel):

    session_id: str

    title: str

    created_at: str

    updated_at: str

    message_count: int


# =========================================================
# Chat History
# =========================================================

def load_history():

    if CHAT_HISTORY_FILE.exists():

        try:

            with open(

                CHAT_HISTORY_FILE,

                "r",

                encoding="utf8"

            ) as f:

                data = json.load(f)

                # Migrate old format to new format with user_id

                migrated = {}

                for session_id, session_data in data.items():

                    if "user_id" not in session_data:

                        session_data["user_id"] = "default"

                    migrated[session_id] = session_data

                return migrated

        except Exception:

            return {}

    return {}


history = load_history()

# Guards reads/writes of `history` so concurrent requests can't corrupt it
_history_lock = threading.RLock()


def save_history():

    with _history_lock, open(

        CHAT_HISTORY_FILE,

        "w",

        encoding="utf8"

    ) as f:

        json.dump(

            history,

            f,

            indent=4,

            ensure_ascii=False

        )


def create_session(user_id: str):

    return uuid.uuid4().hex


def get_session(session_id, user_id: str):

    with _history_lock:

        if session_id not in history:

            history[session_id] = {

                "user_id": user_id,

                "title": "New Chat",

                "created_at": datetime.now().isoformat(),

                "updated_at": datetime.now().isoformat(),

                "messages": []

            }

        return history[session_id]


def add_message(

        session_id,

        role,

        content,

        user_id: str

):

    with _history_lock:

        session = get_session(session_id, user_id)

        session["messages"].append({

            "role": role,

            "content": content,

            "time": datetime.now().isoformat()

        })

        session["updated_at"] = datetime.now().isoformat()

        save_history()


def update_title(session_id, user_id):

    session = get_session(session_id, user_id)

    for msg in session["messages"]:

        if msg["role"] == "user":

            title = msg["content"][:45]

            session["title"] = title

            break

    save_history()

# =========================================================
# Routes
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(

        request=request,
        name="index.html",
        context={

            "request": request,

            "version": "2.0.0",

            "device": DEVICE,

            "knowledge_base": rag_system is not None,

            "load_error": load_error

        }

    )
# =========================================================
# SESSION API
# =========================================================

@app.post("/api/session")
async def create_new_session(user_id: str = ""):
    """Create a new session"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    session_id = create_session(user_id)
    # Initialize the session in history
    get_session(session_id, user_id)
    save_history()
    logger.info(f"Created new session: {session_id} for user: {user_id}")
    return {
        "success": True,
        "session_id": session_id,
        "message": "New session created successfully"
    }

@app.post("/api/session/{session_id}/switch")
async def switch_session(session_id: str, user_id: str = ""):
    """Switch to an existing session"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if session_id not in history:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = history[session_id]
    
    # Verify user owns this session
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    
    session["updated_at"] = datetime.now().isoformat()
    save_history()
    
    logger.info(f"Switched to session: {session_id} for user: {user_id}")
    return {
        "success": True,
        "session_id": session_id,
        "title": session.get("title", "New Chat"),
        "message_count": len(session.get("messages", []))
    }

@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str, user_id: str = ""):
    """Get information about a specific session"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if session_id not in history:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session = history[session_id]
    
    # Verify user owns this session
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    
    return {
        "success": True,
        "session_id": session_id,
        "title": session.get("title", "New Chat"),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
        "message_count": len(session.get("messages", []))
    }

@app.get("/api/sessions")
async def list_all_sessions(user_id: str = ""):
    """List all sessions with metadata for a specific user"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    sessions = []
    for session_id, session in history.items():
        # Only include sessions belonging to this user
        if session.get("user_id") == user_id:
            sessions.append({
                "session_id": session_id,
                "title": session.get("title", "New Chat"),
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at"),
                "message_count": len(session.get("messages", []))
            })
    
    # Sort by updated_at (most recent first)
    sessions.sort(
        key=lambda x: x["updated_at"] or "",
        reverse=True
    )
    
    return {
        "success": True,
        "total": len(sessions),
        "sessions": sessions
    }

# CHAT API
# =========================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):

    global rag_system

    if rag_system is None:

        raise HTTPException(
            status_code=500,
            detail=load_error or "RAG system is not available."
        )

    session_id = request.session_id

    if not session_id:
        session_id = create_session(request.user_id)

    add_message(
        session_id=session_id,
        role="user",
        content=request.message,
        user_id=request.user_id
    )

    try:

        answer = rag_system.run(
            question=request.message,
            session_id=session_id
        )

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    add_message(
        session_id=session_id,
        role="assistant",
        content=answer,
        user_id=request.user_id
    )

    update_title(session_id, request.user_id)

    return {

        "success": True,

        "session_id": session_id,

        "answer": answer,

        "timestamp": datetime.now().isoformat()

    }


# =========================================================
# GET ALL CHATS
# =========================================================

@app.get("/api/history")
async def get_history(user_id: str = ""):

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    chats = []

    for session_id, chat in history.items():

        # Only include chats belonging to this user
        if chat.get("user_id") == user_id:
            chats.append({

                "session_id": session_id,

                "title": chat.get("title", "New Chat"),

                "created_at": chat.get("created_at"),

                "updated_at": chat.get("updated_at"),

                "messages_count": len(
                    chat.get("messages", [])
            )

        })

    chats.sort(

    key=lambda x: x["updated_at"] or "",

    reverse=True

    )

    return chats


# =========================================================
# GET CHAT
# =========================================================

@app.get("/api/history/{session_id}")
async def get_chat(session_id: str, user_id: str = ""):

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if session_id not in history:

        raise HTTPException(

            status_code=404,

            detail="Chat not found."

        )

    chat = history[session_id]
    
    # Verify user owns this chat
    if chat.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return chat


# =========================================================
# RENAME CHAT
# =========================================================

@app.put("/api/history")
async def rename_chat(request: RenameChatRequest, user_id: str = ""):

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    if request.session_id not in history:

        raise HTTPException(

            status_code=404,

            detail="Chat not found."

        )

    chat = history[request.session_id]
    
    # Verify user owns this chat
    if chat.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    chat["title"] = request.title

    chat["updated_at"] = datetime.now().isoformat()

    save_history()

    return {

        "success": True

    }


# =========================================================
# DELETE CHAT
# =========================================================

@app.delete("/api/history/{session_id}")
async def delete_chat(session_id: str, user_id: str = ""):
    """Delete a specific session/chat"""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if session_id not in history:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )
    
    chat = history[session_id]
    
    # Verify user owns this chat
    if chat.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    
    # Get session title before deletion for logging
    session_title = chat.get("title", "New Chat")
    
    # Delete from history
    del history[session_id]
    save_history()
    
    # Clear from RAG system
    if rag_system:
        try:
            rag_system.clear_session(session_id)
        except Exception as e:
            logger.warning(f"Could not clear RAG session {session_id}: {e}")
    
    logger.info(f"Deleted session: {session_id} ('{session_title}') for user: {user_id}")    
    return {
        "success": True,
        "message": f"Session '{session_title}' deleted successfully"
    }


# =========================================================
# CLEAR ALL CHATS
# =========================================================

@app.delete("/api/history")
async def clear_all_history():
    """Delete all sessions/chats"""
    global history

    session_count = len(history)
    history = {}

    save_history()

    if rag_system:
        try:
            rag_system.clear_all_sessions()
        except Exception as e:
            logger.warning(f"Could not clear all RAG sessions: {e}")

    logger.info(f"Deleted all {session_count} sessions")

    return {
        "success": True,
        "message": f"Deleted {session_count} session(s) successfully"
    }


# =========================================================
# STATUS API
# =========================================================

@app.get("/api/status")
async def status():

    return {

        "application": "AI Medical Assistant",

        "version": "2.0.0",

        "status": "online" if rag_system else "offline",

        "device": DEVICE,

        "knowledge_base": rag_system is not None,

        "total_sessions": len(history),

        "server_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    }
# =========================================================
# Upload File
# =========================================================

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):

    extension = Path(file.filename).suffix.lower()

    allowed = [".pdf", ".csv", ".txt"]

    if extension not in allowed:

        raise HTTPException(

            status_code=400,

            detail="Unsupported file type."

        )

    destination = UPLOAD_DIR / file.filename

    with open(destination, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    logger.info(f"Uploaded: {file.filename}")

    return {

        "success": True,

        "filename": file.filename

    }


# =========================================================
# Rebuild Knowledge Base
# =========================================================

@app.post("/api/rebuild")
async def rebuild():

    global rag_system
    global load_error

    try:

        logger.info("Rebuilding Knowledge Base...")

        rag_system = RAGOrchestrator.from_data_directory(

            force_rebuild=True

        )

        logger.info("Knowledge Base rebuilt successfully.")

        return {

            "success": True,

            "message": "Knowledge Base rebuilt successfully."

        }

    except Exception as e:

        load_error = str(e)

        logger.exception(e)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# =========================================================
# Export Chat History
# =========================================================

@app.get("/api/export")
async def export_history():

    return JSONResponse(

        content=history

    )


# =========================================================
# Health Check
# =========================================================

@app.get("/health")
async def health():

    return {

        "status": "ok",

        "application": "AI Medical Assistant",

        "version": "2.0.0",

        "rag_loaded": rag_system is not None,

        "device": DEVICE,

        "total_sessions": len(history),

        "knowledge_base": "Ready" if rag_system else "Offline",

        "server_time": datetime.now().isoformat()

    }


# =========================================================
# API Root
# =========================================================

@app.get("/api")
async def api_root():

    return {

        "name": "AI Medical Assistant",

        "status": "running",

        "version": "2.0.0"

    }


# =========================================================
# Global Exception Handler
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    logger.exception(exc)

    return JSONResponse(

        status_code=500,

        content={

            "success": False,

            "error": str(exc)

        }

    )


# =========================================================
# Startup Info
# =========================================================

@app.on_event("startup")
async def startup_event():

    logger.info("=" * 60)
    logger.info(" AI Medical Assistant Started ")
    logger.info("=" * 60)

    logger.info(f"Device : {DEVICE}")

    logger.info(f"Data Folder : {UPLOAD_DIR}")

    logger.info("=" * 60)


# =========================================================
# Shutdown
# =========================================================

@app.on_event("shutdown")
async def shutdown_event():

    logger.info("Application Shutdown")


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app:app",

        host="127.0.0.1",

        port=8000,

        reload=True

    )