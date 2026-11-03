"""
Retrieval-Augmented Generation (RAG) Pipeline Module.
Orchestrates category filtering, semantic retrieval, prompt assembly,
Gemini generation, and source citation extraction.
"""

import time
from typing import List, Dict, Any, Optional, Tuple

from config.settings import settings
from src.utils import logger, detect_service_category, is_valid_api_key
from src.vector_store import VectorStore
from src.prompts import create_rag_prompt
from src.source_citations import SourceCitation, deduplicate_citations

class RAGPipeline:
    """End-to-end RAG orchestrator for citizen service inquiries."""

    def __init__(self, vector_store: Optional[VectorStore] = None, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.vector_store = vector_store or VectorStore(api_key=self.api_key)
        self.model_name = settings.GEMINI_MODEL
        self._genai_client = None
        self._legacy_client = None
        self._init_llm()

    def update_api_key(self, api_key: str):
        """Allow dynamic API key updates from Streamlit UI."""
        self.api_key = api_key.strip()
        self._init_llm()

    def _init_llm(self):
        """Initialize Google Gemini client using modern google.genai or legacy fallback."""
        if not is_valid_api_key(self.api_key):
            logger.info("RAGPipeline running in local knowledge-base direct mode (no valid API key).")
            self._genai_client = None
            self._legacy_client = None
            return

        try:
            from google import genai
            self._genai_client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized modern google.genai Client for model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed modern google.genai initialization, trying legacy: {e}")
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self._legacy_client = legacy_genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": settings.GEMINI_TEMPERATURE,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )
                logger.info(f"Initialized legacy Gemini LLM model: {self.model_name}")
            except Exception as e2:
                logger.error(f"Error configuring Gemini client: {e2}")

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context chunks with category prioritization."""
        effective_category = category
        if effective_category == "All Services" or not effective_category:
            detected = detect_service_category(query)
            if detected:
                logger.info(f"Auto-detected category: '{detected}' for query: '{query}'")
                effective_category = detected
            else:
                effective_category = None

        return self.vector_store.similarity_search(
            query=query,
            k=top_k,
            category=effective_category
        )

    def extract_citations(self, retrieved_docs: List[Dict[str, Any]]) -> List[SourceCitation]:
        """Convert retrieved document metadata into verified citation models."""
        citations: List[SourceCitation] = []
        for doc in retrieved_docs:
            meta = doc.get("metadata", {})
            title = meta.get("source_title") or meta.get("file_name", "Official Public Document")
            page = meta.get("page_number")
            page_int = int(page) if (page is not None and str(page).isdigit()) else None
            url = meta.get("source_url") or None
            cat = meta.get("category", "Public Services")
            snippet = doc.get("text", "")[:200]
            cid = meta.get("chunk_id")

            citations.append(SourceCitation(
                source_title=title,
                page_number=page_int,
                source_url=url,
                category=cat,
                snippet=snippet,
                chunk_id=cid
            ))

        return deduplicate_citations(citations)

    def _synthesize_local_response(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        language: str = "English"
    ) -> str:
        """
        Fallback response generator when Gemini API key is missing or offline.
        Directly synthesizes verified answers from indexed documents and FAQs.
        """
        if not retrieved_docs:
            if language == "Hindi":
                return "मुझे इस विषय पर आधिकारिक ज्ञानकोष में सत्यापित जानकारी नहीं मिली। कृपया संबंधित सरकारी विभाग या बैंक के आधिकारिक पोर्टल पर संपर्क करें।"
            elif language == "Telugu":
                return "నా దగ్గర ఈ ప్రశ్నకు సంబంధించిన అధికారిక సమాచారం ప్రస్తుతం అందుబాటులో లేదు. దయచేసి సంబంధిత శాఖ అధికారిక పోర్టల్‌ను సంప్రదించండి."
            return "I could not find verified information matching your query in the knowledge base. Please check the official portal or your local department office."

        # Extract answer from the top retrieved document
        top_doc = retrieved_docs[0]
        text = top_doc.get("text", "").strip()
        meta = top_doc.get("metadata", {})
        title = meta.get("source_title", "Official Public Document")

        # Parse FAQ format if present
        clean_body = text
        if "Answer:" in text:
            parts = text.split("Answer:", 1)
            clean_body = parts[1].strip()

        # Format cleanly
        if language == "Hindi":
            header = f"**आधिकारिक जानकारी ({title}):**\n\n"
        elif language == "Telugu":
            header = f"**అధికారిక సమాచారం ({title}):**\n\n"
        else:
            header = f"**Official Information ({title}):**\n\n"

        return f"{header}{clean_body}"

    def generate(
        self,
        query: str,
        category: Optional[str] = "All Services",
        chat_history: Optional[List[Dict[str, str]]] = None,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Execute full RAG generation:
        1. Retrieve top chunks
        2. Format prompt
        3. Call Gemini (or fallback synthesizer)
        4. Package answer with citations, latency, and category metadata
        """
        start_time = time.time()
        chat_history = chat_history or []

        # 1. Retrieval
        retrieved_docs = self.retrieve(query=query, category=category, top_k=settings.TOP_K_RETRIEVAL)
        citations = self.extract_citations(retrieved_docs)

        # 2. Generation via Gemini or Local Fallback
        answer = ""
        is_live_gemini = False

        if (self._genai_client or self._legacy_client) and self.api_key:
            try:
                prompt = create_rag_prompt(
                    user_query=query,
                    retrieved_docs=retrieved_docs,
                    chat_history=chat_history,
                    language=language
                )
                if self._genai_client:
                    clean_model = self.model_name.replace("models/", "")
                    response = self._genai_client.models.generate_content(
                        model=clean_model,
                        contents=prompt
                    )
                else:
                    response = self._legacy_client.generate_content(prompt)

                if response and hasattr(response, 'text') and response.text:
                    answer = response.text.strip()
                    is_live_gemini = True
                else:
                    logger.warning("Empty response received from Gemini API.")
            except Exception as e:
                logger.error(f"Gemini API error during generation: {e}")
                # Fallback to local synthesis
                answer = self._synthesize_local_response(query, retrieved_docs, language)
        else:
            answer = self._synthesize_local_response(query, retrieved_docs, language)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_docs_count": len(retrieved_docs),
            "latency_ms": elapsed_ms,
            "is_live_gemini": is_live_gemini,
            "detected_category": category if category != "All Services" else detect_service_category(query)
        }

