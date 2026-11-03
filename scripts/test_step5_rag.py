"""
QA Verification Script for STEP 5: End-to-End RAG Pipeline Workflow.
Verifies:
1. Ingestion of official PDF
2. Text extraction
3. Splitting into chunks
4. Generating embeddings
5. Storing embeddings in ChromaDB
6. Retrieving relevant chunks
7. Passing context to Gemini
8. Generating grounded answers
9. Displaying citations
10. Handling missing/unrelated queries
11. Persistence of vector DB
"""

import sys
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.document_loader import DocumentLoader
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline

def run_step5_verification():
    print("=" * 80)
    print("STEP 5: END-TO-END RAG PIPELINE VERIFICATION")
    print("=" * 80)

    test_db_dir = "data/step5_test_chroma_db"
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir, ignore_errors=True)

    # 1 & 2. Ingest valid PDF and extract text
    pdf_path = BASE_DIR / "data" / "documents" / "post_office" / "Speed_Post_and_Parcel_Guidelines.pdf"
    assert pdf_path.exists(), f"Sample PDF must exist at {pdf_path}"
    print(f"\n[1] Ingesting PDF: {pdf_path.name}")
    loader = DocumentLoader(chunk_size=500, chunk_overlap=100)
    pdf_chunks = loader.load_pdf(str(pdf_path), category="Post Office Services", source_url="https://www.indiapost.gov.in")
    print(f" -> Extracted {len(pdf_chunks)} chunks from PDF.")
    assert len(pdf_chunks) >= 2, "PDF should produce multiple chunks"

    # 3. Verify metadata & page numbers
    first_chunk = pdf_chunks[0]
    print(f"\n[2] Chunk Metadata Check:")
    print(f" -> Source Title: {first_chunk.metadata.get('source_title')}")
    print(f" -> Page Number:  {first_chunk.metadata.get('page_number')}")
    print(f" -> Category:     {first_chunk.metadata.get('category')}")
    assert first_chunk.metadata.get("page_number") == 1
    assert first_chunk.metadata.get("category") == "Post Office Services"

    # 4 & 5. Store embeddings in ChromaDB
    print(f"\n[3] Initializing isolated ChromaDB at {test_db_dir}...")
    vs = VectorStore(persist_dir=test_db_dir, collection_name="step5_collection")
    added_count = vs.add_chunks(pdf_chunks)
    print(f" -> Successfully stored {added_count} chunks in ChromaDB.")
    assert vs.count() == len(pdf_chunks)

    # 6. Retrieve relevant chunks
    rag = RAGPipeline(vector_store=vs)
    query = "What is the maximum weight limit for Speed Post parcels?"
    print(f"\n[4] Semantic Retrieval for Query: '{query}'")
    retrieved = rag.retrieve(query=query, category="Post Office Services", top_k=2)
    print(f" -> Retrieved {len(retrieved)} relevant chunks.")
    assert len(retrieved) >= 1
    retrieved_text = " ".join([d["text"] for d in retrieved])
    print(f" -> Text excerpt: {retrieved_text[:180]}...")
    assert "35" in retrieved_text or "weight" in retrieved_text.lower(), "Retrieved chunk must contain weight limit details"

    # 7, 8 & 9. Context passing, grounded generation & source citations
    print(f"\n[5] Generating Grounded Answer with Citations...")
    gen_result = rag.generate(query=query, category="Post Office Services")
    print(f" -> Answer:\n{gen_result['answer']}\n")
    citations = gen_result["citations"]
    print(f" -> Citations ({len(citations)}):")
    for c in citations:
        print(f"    • {c.source_title} (Page {c.page_number}) - {c.source_url}")
    assert len(citations) >= 1
    assert citations[0].page_number == 1
    assert "35" in gen_result["answer"] or "weight" in gen_result["answer"].lower()

    # 10. Handle query with no relevant documents
    irrelevant_query = "How do I build a nuclear reactor in my backyard?"
    print(f"\n[6] Testing Irrelevant Query Handling: '{irrelevant_query}'")
    irrel_result = rag.generate(query=irrelevant_query, category="Post Office Services")
    print(f" -> Response:\n{irrel_result['answer'][:250]}...\n")
    assert any(term in irrel_result["answer"].lower() for term in ["cannot be verified", "not contain", "not have verified", "could not find", "official portal", "please check"]), "Must gracefully report lack of verified information"

    # 11. Test vector DB persistence
    print(f"\n[7] Testing Vector Database Persistence...")
    del vs
    vs_reopened = VectorStore(persist_dir=test_db_dir, collection_name="step5_collection")
    reopened_count = vs_reopened.count()
    print(f" -> Reopened collection count: {reopened_count} (Expected: {len(pdf_chunks)})")
    assert reopened_count == len(pdf_chunks)

    # Clean up test DB
    if os.path.exists(test_db_dir):
        shutil.rmtree(test_db_dir, ignore_errors=True)

    print("\n" + "=" * 80)
    print("STEP 5: ALL RAG PIPELINE VERIFICATION TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    run_step5_verification()

