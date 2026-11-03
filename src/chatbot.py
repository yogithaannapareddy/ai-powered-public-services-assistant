"""
Chatbot Conversational Engine.
Maintains session state, multi-turn dialogue memory,
handles follow-up queries, and delegates to the RAG pipeline.
"""

from typing import List, Dict, Any, Optional
from src.rag_pipeline import RAGPipeline
from src.source_citations import SourceCitation
from src.utils import logger

class Chatbot:
    """Manages conversational dialogue and delegates answering to RAGPipeline."""

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        self.rag = rag_pipeline or RAGPipeline()
        self.conversation_history: List[Dict[str, str]] = []

    def clear_history(self):
        """Reset conversation memory."""
        self.conversation_history = []
        logger.info("Chat history cleared.")

    def ask(
        self,
        user_message: str,
        category: str = "All Services",
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Process user message through RAG pipeline, appending user and assistant messages
        to conversational memory.
        """
        clean_msg = user_message.strip()
        if not clean_msg:
            return {
                "answer": "Please ask a question regarding public services.",
                "citations": [],
                "latency_ms": 0,
                "is_live_gemini": False
            }

        # Invoke RAG pipeline with conversation history
        rag_result = self.rag.generate(
            query=clean_msg,
            category=category,
            chat_history=self.conversation_history,
            language=language
        )

        answer = rag_result.get("answer", "")

        # Store turn in memory
        self.conversation_history.append({"role": "user", "content": clean_msg})
        self.conversation_history.append({"role": "assistant", "content": answer})

        return rag_result

    def get_history(self) -> List[Dict[str, str]]:
        """Return the current conversation history."""
        return self.conversation_history
