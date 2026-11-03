"""
Optional FastAPI Backend Service for AI-Powered Public Services Assistant.
Provides RESTful endpoints for integration into mobile apps, web portals, or external clients.
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config.settings import settings
from src.chatbot import Chatbot
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore
from src.language_support import get_text

app = FastAPI(
    title="AI-Powered Public Services Assistant API",
    description="REST API for citizen public services guidance in India (Post Office, Banking, Transport, Government).",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy singleton
_rag_pipeline: Optional[RAGPipeline] = None

def get_rag() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        vs = VectorStore()
        _rag_pipeline = RAGPipeline(vector_store=vs)
    return _rag_pipeline

# Request & Response Models
class ChatRequest(BaseModel):
    query: str = Field(..., description="Citizen inquiry question", example="How do I send a parcel to another state?")
    category: Optional[str] = Field("All Services", description="Selected public service category")
    language: Optional[str] = Field("English", description="Target language (English, Hindi, Telugu)")
    chat_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Previous conversation turns")

class CitationModel(BaseModel):
    source_title: str
    page_number: Optional[int] = None
    source_url: Optional[str] = None
    category: str
    snippet: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationModel]
    latency_ms: int
    is_live_gemini: bool
    detected_category: Optional[str]

@app.get("/health")
def health_check():
    rag = get_rag()
    return {
        "status": "healthy",
        "service": "AI-Powered Public Services Assistant",
        "total_indexed_chunks": rag.vector_store.count(),
        "gemini_configured": bool(rag.api_key)
    }

@app.get("/api/categories")
def get_categories():
    return {
        "categories": settings.CATEGORIES,
        "languages": list(settings.SUPPORTED_LANGUAGES.keys())
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    rag = get_rag()
    result = rag.generate(
        query=request.query,
        category=request.category,
        chat_history=request.chat_history,
        language=request.language
    )
    
    citations = [
        CitationModel(
            source_title=c.source_title,
            page_number=c.page_number,
            source_url=c.source_url,
            category=c.category,
            snippet=c.snippet
        )
        for c in result.get("citations", [])
    ]
    
    return ChatResponse(
        answer=result.get("answer", ""),
        citations=citations,
        latency_ms=result.get("latency_ms", 0),
        is_live_gemini=result.get("is_live_gemini", False),
        detected_category=result.get("detected_category")
    )
