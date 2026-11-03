import re
import logging
from typing import Optional, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("public_services_assistant")

def clean_text(text: str) -> str:
    """Normalize whitespace and strip unprintable characters."""
    if not text:
        return ""
    # Replace non-breaking spaces and carriage returns
    text = text.replace('\xa0', ' ').replace('\r', '')
    # Strip whitespace from each line and compress multiple spaces
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    cleaned = '\n'.join(lines)
    # Collapse 3 or more newlines into double newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def sanitize_filename(name: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', Path(name).name)
    return clean_name or "uploaded_document"

def validate_uploaded_file(file_name: str, file_size_bytes: int, max_size_mb: int = 10) -> Tuple[bool, str]:
    """Validate uploaded document format and size limit."""
    allowed_extensions = {".pdf", ".txt", ".json", ".md"}
    ext = Path(file_name).suffix.lower()
    
    if ext not in allowed_extensions:
        return False, f"Unsupported file type '{ext}'. Allowed types: PDF, TXT, JSON, MD."
        
    max_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File size exceeds maximum allowed limit of {max_size_mb} MB (Uploaded: {file_size_bytes / (1024*1024):.2f} MB)."
        
    if file_size_bytes == 0:
        return False, "File is empty."
        
    return True, "Valid"

def detect_service_category(query: str) -> Optional[str]:
    """Detect probable public service category from user query keywords."""
    query_lower = query.lower()
    
    # Post office keywords
    po_keywords = [
        "speed post", "parcel", "post office", "postal", "pincode", "pin code",
        "postman", "dak", "ippb", "savings certificate", "posa", "sukanya samriddhi",
        "national savings certificate", "postage", "consignment"
    ]
    if any(kw in query_lower for kw in po_keywords):
        return "Post Office Services"
        
    # Banking keywords
    bank_keywords = [
        "bank", "account opening", "kyc", "debit card", "atm", "upi", "pin",
        "cheque", "loan", "interest rate", "passbook", "rbi", "ombudsman",
        "fixed deposit", "savings account", "bsbda", "jan dhan", "cyber fraud",
        "net banking", "mobile banking"
    ]
    if any(kw in query_lower for kw in bank_keywords):
        return "Banking Services"
        
    # Transportation keywords
    trans_keywords = [
        "train", "irctc", "railway", "tatkal", "bus pass", "bus", "metro",
        "ncmc", "pnr", "ticket", "reservation", "sleeper", "coach", "depot",
        "smart card", "tsrtc", "apsrtc", "dtc", "bmtc", "msrtc"
    ]
    if any(kw in query_lower for kw in trans_keywords):
        return "Public Transportation"
        
    # Government services keywords
    gov_keywords = [
        "certificate", "income certificate", "caste certificate", "domicile",
        "residence certificate", "digilocker", "birth certificate", "death certificate",
        "ration card", "aadhaar", "pan card", "serviceplus", "meeseva", "edistrict",
        "tahsildar", "sdm", "government scheme", "scholarship", "portal"
    ]
    if any(kw in query_lower for kw in gov_keywords):
        return "Government Services"
        
    return None
