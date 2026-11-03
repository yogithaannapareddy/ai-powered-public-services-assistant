import pytest
from pathlib import Path
from src.document_loader import DocumentLoader, DocumentChunk
from src.utils import validate_uploaded_file, clean_text

def test_clean_text():
    raw = "  Hello   world \xa0! \n\n\n\n Next line.  "
    cleaned = clean_text(raw)
    assert cleaned == "Hello world !\n\nNext line."

def test_validate_uploaded_file_valid():
    valid, msg = validate_uploaded_file("document.pdf", 1024 * 500, max_size_mb=10)
    assert valid is True
    assert msg == "Valid"

def test_validate_uploaded_file_invalid_extension():
    valid, msg = validate_uploaded_file("malicious.exe", 1024, max_size_mb=10)
    assert valid is False
    assert "Unsupported file type" in msg

def test_validate_uploaded_file_too_large():
    valid, msg = validate_uploaded_file("large.pdf", 15 * 1024 * 1024, max_size_mb=10)
    assert valid is False
    assert "exceeds maximum allowed limit" in msg

def test_validate_uploaded_file_empty():
    valid, msg = validate_uploaded_file("empty.pdf", 0, max_size_mb=10)
    assert valid is False
    assert "empty" in msg.lower()

def test_chunk_text():
    loader = DocumentLoader(chunk_size=100, chunk_overlap=20)
    text = (
        "Speed Post is an express postal service in India. "
        "It provides fast parcel delivery across all states. "
        "You can track your speed post with a 13 character tracking ID. "
        "Post offices also offer savings accounts."
    )
    chunks = loader.chunk_text(text, base_metadata={"source_title": "Test Guide", "category": "Post Office Services"})
    
    assert len(chunks) >= 1
    for chunk in chunks:
        assert isinstance(chunk, DocumentChunk)
        assert chunk.metadata["source_title"] == "Test Guide"
        assert chunk.metadata["category"] == "Post Office Services"
        assert "chunk_id" in chunk.metadata
        assert len(chunk.text) > 20

def test_load_faq_json():
    loader = DocumentLoader()
    faq_path = Path("data/faqs/post_office_faq.json")
    assert faq_path.exists(), "Sample post_office_faq.json must exist"
    
    chunks = loader.load_faq_json(str(faq_path))
    assert len(chunks) >= 3
    assert any("Speed Post" in c.text for c in chunks)
    assert chunks[0].metadata["category"] == "Post Office Services"
    assert chunks[0].metadata["source_url"] != ""

def test_load_pdf():
    loader = DocumentLoader()
    pdf_path = Path("data/documents/post_office/Speed_Post_and_Parcel_Guidelines.pdf")
    assert pdf_path.exists(), "Generated sample PDF must exist"
    
    chunks = loader.load_pdf(str(pdf_path), category="Post Office Services")
    assert len(chunks) >= 1
    assert chunks[0].metadata["file_type"] == "pdf"
    assert chunks[0].metadata["page_number"] >= 1
    assert any("Speed Post" in c.text or "parcel" in c.text.lower() for c in chunks)

def test_load_text_file():
    loader = DocumentLoader()
    txt_path = Path("data/documents/banking/rbi_kyc_and_digital_banking_guide.txt")
    assert txt_path.exists(), "Sample banking text guide must exist"
    
    chunks = loader.load_text_file(str(txt_path), category="Banking Services")
    assert len(chunks) >= 1
    assert chunks[0].metadata["category"] == "Banking Services"
    assert any("KYC" in c.text for c in chunks)

