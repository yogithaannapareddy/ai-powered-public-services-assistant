import os
import shutil
import pytest
from src.vector_store import VectorStore
from src.document_loader import DocumentChunk
from src.source_citations import SourceCitation, deduplicate_citations, format_citations_markdown
from src.rag_pipeline import RAGPipeline

TEST_DB_DIR = "data/test_chroma_db"

@pytest.fixture(scope="module")
def setup_test_vector_store():
    # Setup clean test vector store
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR, ignore_errors=True)
        
    vs = VectorStore(persist_dir=TEST_DB_DIR, collection_name="test_collection")
    
    # Create sample chunks across categories
    chunks = [
        DocumentChunk(
            text="Speed Post delivery takes 1 to 3 days between major metro cities in India.",
            metadata={
                "source_title": "Speed Post Charter",
                "page_number": 1,
                "category": "Post Office Services",
                "source_url": "https://www.indiapost.gov.in",
                "chunk_id": "test_po_1"
            }
        ),
        DocumentChunk(
            text="To open a savings bank account, submit PAN card, Aadhaar card, and two passport photos.",
            metadata={
                "source_title": "RBI Account Opening Norms",
                "page_number": 2,
                "category": "Banking Services",
                "source_url": "https://www.rbi.org.in",
                "chunk_id": "test_bank_1"
            }
        ),
        DocumentChunk(
            text="Tatkal train tickets open at 10 AM for AC classes and 11 AM for Sleeper class one day before departure.",
            metadata={
                "source_title": "IRCTC Tatkal Booking Rules",
                "page_number": 1,
                "category": "Public Transportation",
                "source_url": "https://www.irctc.co.in",
                "chunk_id": "test_trans_1"
            }
        ),
        DocumentChunk(
            text="Income certificates are issued by Tahsildar through ServicePlus portal within 15 days.",
            metadata={
                "source_title": "ServicePlus Portal Manual",
                "page_number": 3,
                "category": "Government Services",
                "source_url": "https://serviceonline.gov.in",
                "chunk_id": "test_gov_1"
            }
        )
    ]
    vs.add_chunks(chunks)
    yield vs
    
    # Teardown
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR, ignore_errors=True)

def test_vector_store_count(setup_test_vector_store):
    vs = setup_test_vector_store
    assert vs.count() == 4

def test_similarity_search_unfiltered(setup_test_vector_store):
    vs = setup_test_vector_store
    results = vs.similarity_search("How do I book Tatkal tickets?", k=2)
    assert len(results) >= 1
    assert "Tatkal" in results[0]["text"]
    assert results[0]["metadata"]["category"] == "Public Transportation"

def test_similarity_search_category_filter(setup_test_vector_store):
    vs = setup_test_vector_store
    results = vs.similarity_search("documents required", k=2, category="Banking Services")
    assert len(results) >= 1
    assert results[0]["metadata"]["category"] == "Banking Services"
    assert "Aadhaar" in results[0]["text"]

def test_source_citation_deduplication():
    c1 = SourceCitation(
        source_title="India Post Guidelines",
        page_number=1,
        source_url="https://indiapost.gov.in",
        category="Post Office Services"
    )
    c2 = SourceCitation(
        source_title="India Post Guidelines",
        page_number=1,
        source_url="https://indiapost.gov.in",
        category="Post Office Services"
    )
    c3 = SourceCitation(
        source_title="India Post Guidelines",
        page_number=2,
        source_url="https://indiapost.gov.in",
        category="Post Office Services"
    )
    
    deduped = deduplicate_citations([c1, c2, c3])
    assert len(deduped) == 2
    md = format_citations_markdown(deduped)
    assert "India Post Guidelines" in md
    assert "Page 1" in md
    assert "Page 2" in md

def test_rag_pipeline_generation(setup_test_vector_store):
    vs = setup_test_vector_store
    rag = RAGPipeline(vector_store=vs, api_key="")
    
    res = rag.generate("When does Tatkal booking open?", category="Public Transportation")
    assert "answer" in res
    assert len(res["citations"]) >= 1
    assert res["citations"][0].source_title == "IRCTC Tatkal Booking Rules"
    assert res["latency_ms"] >= 0
