"""
Document Loader and Processing Module.
Extracts text from PDF, TXT, MD, and JSON FAQ files, cleans content,
and creates semantically coherent chunks with preserved metadata.
"""

import os
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import pypdf

from config.settings import settings
from src.utils import clean_text, logger

class DocumentChunk:
    """Represents a discrete chunk of text with rich metadata."""
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return f"<DocumentChunk title={self.metadata.get('source_title')} page={self.metadata.get('page_number')}>"


class DocumentLoader:
    """Loads and chunks documents from various formats with metadata preservation."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split text into overlapping chunks while preserving sentence boundaries."""
        cleaned = clean_text(text)
        if not cleaned:
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        total_len = len(cleaned)

        while start < total_len:
            end = start + self.chunk_size

            # If not at the end of the text, try to find a sentence or newline break
            if end < total_len:
                # Look for paragraph break first, then period/question mark, then space
                break_point = -1
                for punct in ['\n\n', '. ', '? ', '! ', '\n', ' ']:
                    pos = cleaned.rfind(punct, start + int(self.chunk_size * 0.6), end)
                    if pos != -1:
                        break_point = pos + len(punct)
                        break
                if break_point != -1:
                    end = break_point

            chunk_content = cleaned[start:end].strip()
            if len(chunk_content) >= 40:  # Avoid empty or tiny fragments
                chunk_meta = dict(base_metadata)
                chunk_meta["chunk_id"] = str(uuid.uuid4())
                chunk_meta["char_start"] = start
                chunk_meta["char_end"] = end
                chunks.append(DocumentChunk(text=chunk_content, metadata=chunk_meta))

            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def load_pdf(self, file_path: str, category: str = "General", source_url: Optional[str] = None) -> List[DocumentChunk]:
        """Extract text from PDF page by page using pypdf and generate chunks."""
        chunks: List[DocumentChunk] = []
        path = Path(file_path)
        source_title = path.stem.replace("_", " ").title()

        try:
            reader = pypdf.PdfReader(str(path))
            total_pages = len(reader.pages)
            logger.info(f"Loading PDF '{path.name}' with {total_pages} pages")

            for page_idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    continue

                base_meta = {
                    "source_title": source_title,
                    "file_name": path.name,
                    "page_number": page_idx,
                    "total_pages": total_pages,
                    "category": category,
                    "source_url": source_url or "",
                    "file_type": "pdf"
                }

                page_chunks = self.chunk_text(page_text, base_meta)
                chunks.extend(page_chunks)

        except Exception as e:
            logger.error(f"Error loading PDF '{file_path}': {e}")
            raise e

        return chunks

    def load_pdf_bytes(self, pdf_bytes: bytes, file_name: str, category: str = "General", source_url: Optional[str] = None) -> List[DocumentChunk]:
        """Extract and chunk PDF from memory bytes (for Streamlit file uploads)."""
        import io
        chunks: List[DocumentChunk] = []
        source_title = Path(file_name).stem.replace("_", " ").title()

        try:
            stream = io.BytesIO(pdf_bytes)
            reader = pypdf.PdfReader(stream)
            total_pages = len(reader.pages)

            for page_idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    continue

                base_meta = {
                    "source_title": source_title,
                    "file_name": file_name,
                    "page_number": page_idx,
                    "total_pages": total_pages,
                    "category": category,
                    "source_url": source_url or "",
                    "file_type": "pdf"
                }

                page_chunks = self.chunk_text(page_text, base_meta)
                chunks.extend(page_chunks)

        except Exception as e:
            logger.error(f"Error parsing in-memory PDF '{file_name}': {e}")
            raise e

        return chunks

    def load_text_file(self, file_path: str, category: str = "General", source_url: Optional[str] = None) -> List[DocumentChunk]:
        """Load standard text or markdown document and chunk it."""
        path = Path(file_path)
        source_title = path.stem.replace("_", " ").title()

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            base_meta = {
                "source_title": source_title,
                "file_name": path.name,
                "page_number": 1,
                "category": category,
                "source_url": source_url or "",
                "file_type": path.suffix.lstrip(".").lower()
            }

            return self.chunk_text(content, base_meta)
        except Exception as e:
            logger.error(f"Error reading text file '{file_path}': {e}")
            raise e

    def load_faq_json(self, file_path: str) -> List[DocumentChunk]:
        """Parse structured FAQ JSON file into standalone queryable chunks."""
        chunks: List[DocumentChunk] = []
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                faqs = json.load(f)

            if not isinstance(faqs, list):
                logger.warning(f"FAQ file '{path.name}' does not contain a JSON array.")
                return []

            for faq in faqs:
                q = faq.get("question", "").strip()
                a = faq.get("answer", "").strip()
                docs = faq.get("documents_required", [])
                docs_text = f"\nRequired Documents: {', '.join(docs)}" if docs else ""
                
                content = f"Question: {q}\nAnswer: {a}{docs_text}"
                
                meta = {
                    "source_title": faq.get("source_title", path.stem.replace("_", " ").title()),
                    "file_name": path.name,
                    "page_number": 1,
                    "category": faq.get("category", "General"),
                    "source_url": faq.get("source_url", ""),
                    "service": faq.get("service", ""),
                    "faq_id": faq.get("id", str(uuid.uuid4())),
                    "chunk_id": str(uuid.uuid4()),
                    "file_type": "json_faq"
                }
                chunks.append(DocumentChunk(text=content, metadata=meta))

        except Exception as e:
            logger.error(f"Error reading FAQ JSON '{file_path}': {e}")
            raise e

        return chunks

    def load_all_sample_knowledge(self, data_dir: Optional[Path] = None) -> List[DocumentChunk]:
        """Walk the data/ directory and ingest all PDFs, text guides, and FAQ JSON files."""
        from config.settings import DATA_DIR
        base_dir = data_dir or DATA_DIR
        all_chunks: List[DocumentChunk] = []

        # 1. Load FAQs
        faqs_dir = base_dir / "faqs"
        if faqs_dir.exists():
            for faq_file in faqs_dir.glob("*.json"):
                logger.info(f"Ingesting FAQ: {faq_file.name}")
                chunks = self.load_faq_json(str(faq_file))
                all_chunks.extend(chunks)

        # 2. Category Document Directories
        category_mapping = {
            "post_office": "Post Office Services",
            "banking": "Banking Services",
            "transportation": "Public Transportation",
            "government": "Government Services"
        }

        docs_dir = base_dir / "documents"
        if docs_dir.exists():
            for folder, cat_name in category_mapping.items():
                folder_path = docs_dir / folder
                if not folder_path.exists():
                    continue

                # Load PDFs
                for pdf_file in folder_path.glob("*.pdf"):
                    logger.info(f"Ingesting PDF: {pdf_file.name} in {cat_name}")
                    chunks = self.load_pdf(str(pdf_file), category=cat_name)
                    all_chunks.extend(chunks)

                # Load TXT and MD files
                for txt_file in folder_path.glob("*.[tT][xX][tT]"):
                    logger.info(f"Ingesting Text: {txt_file.name} in {cat_name}")
                    chunks = self.load_text_file(str(txt_file), category=cat_name)
                    all_chunks.extend(chunks)

        logger.info(f"Total knowledge base chunks created: {len(all_chunks)}")
        return all_chunks

