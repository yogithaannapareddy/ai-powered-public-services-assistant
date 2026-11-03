"""
Embedding Generation Module for Vector Store.
Supports Google Gemini Embedding API (models/text-embedding-004)
with fallback to local SentenceTransformers or Chroma Default Embedding.
"""

from typing import List, Union
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from config.settings import settings
from src.utils import logger

class GeminiEmbeddingFunction(EmbeddingFunction):
    """ChromaDB compatible embedding function utilizing Google Gemini API."""

    def __init__(self, api_key: str = "", model_name: str = "models/text-embedding-004"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_EMBEDDING_MODEL
        self._client = None
        self._init_client()

    def name(self) -> str:
        return f"gemini_{self.model_name.replace('/', '_')}"

    def get_config(self) -> dict:
        return {"model_name": self.model_name}

    def _init_client(self):
        if not self.api_key:
            logger.warning("No Gemini API key supplied for GeminiEmbeddingFunction.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
            logger.info(f"Initialized Gemini Embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embedding client: {e}")
            self._client = None

    def __call__(self, input: Documents) -> Embeddings:
        """Embed a list of text strings using Gemini API."""
        if not self._client or not self.api_key:
            raise RuntimeError("Gemini API key is not configured for embeddings.")

        embeddings: List[List[float]] = []
        # Batch requests in groups of 16 to respect API limits
        batch_size = 16
        for i in range(0, len(input), batch_size):
            batch = input[i:i + batch_size]
            try:
                # Use genai.embed_content
                result = self._client.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                if "embedding" in result:
                    batch_embeddings = result["embedding"]
                    # If single item batch, it may be a flat list
                    if batch_embeddings and isinstance(batch_embeddings[0], (int, float)):
                        batch_embeddings = [batch_embeddings]
                    embeddings.extend(batch_embeddings)
                else:
                    raise ValueError("No 'embedding' key returned from Gemini API.")
            except Exception as e:
                logger.error(f"Error calling Gemini Embedding API on batch {i}: {e}")
                raise e

        return embeddings


class LocalFallbackEmbeddingFunction(EmbeddingFunction):
    """ChromaDB default local embedding function (Sentence-Transformers / ONNX MiniLM)."""

    def __init__(self):
        self._ef = None
        self._init_local()

    def name(self) -> str:
        return "local_minilm_l6_v2"

    def get_config(self) -> dict:
        return {"model": "all-MiniLM-L6-v2"}

    def _init_local(self):
        try:
            from chromadb.utils import embedding_functions
            self._ef = embedding_functions.DefaultEmbeddingFunction()
            logger.info("Initialized Chroma default local embedding function (all-MiniLM-L6-v2 ONNX).")
        except Exception as e:
            logger.warning(f"Could not initialize Chroma DefaultEmbeddingFunction: {e}")
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('all-MiniLM-L6-v2')
                self._ef = lambda docs: model.encode(docs).tolist()
                logger.info("Initialized SentenceTransformer fallback.")
            except Exception as e2:
                logger.error(f"Failed all local embedding initializations: {e2}")
                self._ef = None

    def __call__(self, input: Documents) -> Embeddings:
        if self._ef is None:
            raise RuntimeError("No local embedding function available.")
        return self._ef(input)


def get_embedding_function(api_key: str = "", force_local: bool = False) -> EmbeddingFunction:
    """
    Factory function to get the appropriate embedding function.
    Prefers Gemini if API key is provided and force_local is False;
    otherwise falls back to Chroma's local embedding function.
    """
    active_key = api_key or settings.GEMINI_API_KEY
    if active_key and not force_local and settings.EMBEDDING_PROVIDER == "gemini":
        try:
            # Test instantiation
            gemini_ef = GeminiEmbeddingFunction(api_key=active_key)
            if gemini_ef._client:
                return gemini_ef
        except Exception as e:
            logger.warning(f"Failed initializing Gemini embeddings, using local fallback: {e}")

    logger.info("Using local fallback embedding function.")
    return LocalFallbackEmbeddingFunction()
