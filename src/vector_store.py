"""
Vector Store Management Module using ChromaDB.
Handles persistence, batch document indexing, deduplication,
and category-aware semantic similarity search.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from src.embeddings import get_embedding_function
from src.document_loader import DocumentChunk
from src.utils import logger

class VectorStore:
    """Manages ChromaDB vector database collections and semantic retrieval."""

    def __init__(self, persist_dir: Optional[str] = None, collection_name: Optional[str] = None, api_key: str = ""):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.api_key = api_key or settings.GEMINI_API_KEY
        
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedding_fn = get_embedding_function(api_key=self.api_key)
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        """Retrieve or create persistent Chroma collection with embedding function."""
        try:
            return self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "Citizen Public Services Knowledge Collection"}
            )
        except Exception as e:
            logger.error(f"Error accessing Chroma collection '{self.collection_name}': {e}")
            raise e

    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = 50) -> int:
        """
        Add document chunks to vector store in batches with metadata and deduplication.
        Returns the count of successfully inserted chunks.
        """
        if not chunks:
            return 0

        total_added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            ids = []
            documents = []
            metadatas = []

            for chunk in batch:
                cid = chunk.metadata.get("chunk_id") or f"doc_{total_added}_{i}"
                ids.append(cid)
                documents.append(chunk.text)
                
                # Chroma metadata values must be str, int, float, or bool
                clean_meta = {}
                for k, v in chunk.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    elif v is None:
                        clean_meta[k] = ""
                    else:
                        clean_meta[k] = str(v)
                metadatas.append(clean_meta)

            try:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                total_added += len(batch)
            except Exception as e:
                logger.error(f"Failed to upsert batch into ChromaDB: {e}")
                raise e

        logger.info(f"Successfully indexed {total_added} chunks into '{self.collection_name}'")
        return total_added

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity retrieval on vector store.
        If category is specified and not 'All Services', applies metadata filtering.
        """
        where_clause = None
        if category and category != "All Services":
            where_clause = {"category": category}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=where_clause
            )
            # If filtered search yielded 0 documents, fall back to global search
            if where_clause and (not results or not results.get("documents") or not results["documents"][0]):
                logger.info("Category-filtered search yielded 0 documents; falling back to global search.")
                results = self.collection.query(
                    query_texts=[query],
                    n_results=k
                )
        except Exception as e:
            logger.warning(f"Chroma filtered search failed ({e}), falling back to unfiltered search.")
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )

        retrieved_docs: List[Dict[str, Any]] = []
        if not results or not results.get("documents") or not results["documents"][0]:
            return retrieved_docs

        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
        ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

        for text, meta, dist, cid in zip(docs, metadatas, distances, ids):
            retrieved_docs.append({
                "text": text,
                "metadata": meta,
                "distance": dist,
                "id": cid
            })

        return retrieved_docs

    def count(self) -> int:
        """Return total number of chunks indexed in the collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    def reset(self):
        """Delete collection to re-index fresh knowledge base."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.get_or_create_collection()
            logger.info(f"Reset Chroma collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")

