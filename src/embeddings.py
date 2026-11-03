"""
Embedding Generation Module for Vector Store.
Supports Google Gemini Embedding API (models/text-embedding-004)
with fallback to local SentenceTransformers or Chroma Default Embedding.
"""

from typing import List, Union, Optional
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from config.settings import settings
from src.utils import logger, is_valid_api_key

class GeminiEmbeddingFunction(EmbeddingFunction):
    """ChromaDB compatible embedding function utilizing Google Gemini API."""

    def __init__(self, api_key: str = "", model_name: str = "models/text-embedding-004"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_EMBEDDING_MODEL
        self._genai_client = None
        self._legacy_client = None
        self._init_client()

    @staticmethod
    def name() -> str:
        return "gemini_text_embedding_004"

    def get_config(self) -> dict:
        return {"model_name": self.model_name}

    @staticmethod
    def build_from_config(config: dict) -> "GeminiEmbeddingFunction":
        return GeminiEmbeddingFunction(model_name=config.get("model_name", "models/text-embedding-004"))

    def _init_client(self):
        if not is_valid_api_key(self.api_key):
            logger.info("No valid Gemini API key supplied for GeminiEmbeddingFunction.")
            return

        try:
            from google import genai
            self._genai_client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized modern google.genai Client for embedding: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed modern google.genai embedding client, falling back: {e}")
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self._legacy_client = legacy_genai
                logger.info(f"Initialized legacy Gemini embedding client: {self.model_name}")
            except Exception as e2:
                logger.error(f"Failed to initialize any Gemini embedding client: {e2}")

    def __call__(self, input: Documents) -> Embeddings:
        """Embed a list of text strings using Gemini API."""
        if not self._genai_client and not self._legacy_client:
            raise RuntimeError("Gemini API key is not configured for embeddings.")

        embeddings: List[List[float]] = []
        batch_size = 16
        for i in range(0, len(input), batch_size):
            batch = input[i:i + batch_size]
            try:
                if self._genai_client:
                    clean_model = self.model_name.replace("models/", "")
                    res = self._genai_client.models.embed_content(
                        model=clean_model,
                        contents=batch
                    )
                    if hasattr(res, "embeddings") and res.embeddings:
                        embeddings.extend([e.values for e in res.embeddings])
                    else:
                        raise ValueError("No embeddings found in response from modern google.genai.")
                elif self._legacy_client:
                    result = self._legacy_client.embed_content(
                        model=self.model_name,
                        content=batch,
                        task_type="retrieval_document"
                    )
                    if "embedding" in result:
                        batch_embeddings = result["embedding"]
                        if batch_embeddings and isinstance(batch_embeddings[0], (int, float)):
                            batch_embeddings = [batch_embeddings]
                        embeddings.extend(batch_embeddings)
                    else:
                        raise ValueError("No 'embedding' key returned from legacy Gemini API.")
            except Exception as e:
                logger.error(f"Error calling Gemini Embedding API on batch {i}: {e}")
                raise e

        return embeddings


class LocalFallbackEmbeddingFunction(EmbeddingFunction):
    """ChromaDB default local embedding function (Sentence-Transformers / ONNX MiniLM)."""

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model = model
        self._ef = None
        self._init_local()

    @staticmethod
    def name() -> str:
        return "local_minilm_l6_v2"

    def get_config(self) -> dict:
        return {"model": self.model}

    @staticmethod
    def build_from_config(config: dict) -> "LocalFallbackEmbeddingFunction":
        return LocalFallbackEmbeddingFunction(model=config.get("model", "all-MiniLM-L6-v2"))

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


def get_embedding_function(api_key: Optional[str] = None, force_local: bool = False) -> EmbeddingFunction:
    """
    Factory function to get the appropriate embedding function.
    Uses Gemini embeddings when EMBEDDING_PROVIDER is 'gemini', API key is valid,
    and connectivity succeeds; otherwise falls back gracefully to local ONNX MiniLM.
    """
    active_key = api_key if api_key is not None else settings.GEMINI_API_KEY
    if is_valid_api_key(active_key) and not force_local and settings.EMBEDDING_PROVIDER.lower() == "gemini":
        try:
            gemini_ef = GeminiEmbeddingFunction(api_key=active_key)
            if gemini_ef._genai_client or gemini_ef._legacy_client:
                # Test connectivity with a single token
                gemini_ef(["test"])
                return gemini_ef
        except Exception as e:
            logger.warning(f"Gemini embedding API verification failed ({e}); falling back to local embeddings.")

    return LocalFallbackEmbeddingFunction()
