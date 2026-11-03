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

def is_valid_api_key(key: Optional[str]) -> bool:
    """Validate whether an API key is a genuine key rather than empty or placeholder."""
    if not key:
        return False
    k = key.strip()
    placeholder_keys = {
        "your_gemini_api_key_here",
        "your_api_key_here",
        "your_key_here",
        "placeholder",
        "none",
        ""
    }
    if k.lower() in placeholder_keys:
        return False
    return len(k) >= 12

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
    
    # Post office keywords (English, Hindi, Telugu)
    po_keywords = [
        "speed post", "parcel", "post office", "postal", "pincode", "pin code",
        "postman", "dak", "ippb", "savings certificate", "posa", "sukanya samriddhi",
        "national savings certificate", "postage", "consignment",
        "पार्सल", "स्पीड पोस्ट", "डाक", "डाकघर", "పార్శిల్‌", "స్పీడ్ పోస్ట్", "తపాలా", "పోస్టాఫీస్", "పోస్ట్"
    ]
    if any(kw in query_lower for kw in po_keywords):
        return "Post Office Services"
        
    # Banking keywords (English, Hindi, Telugu)
    bank_keywords = [
        "bank", "account opening", "kyc", "debit card", "atm", "upi", "pin",
        "cheque", "loan", "interest rate", "passbook", "rbi", "ombudsman",
        "fixed deposit", "savings account", "bsbda", "jan dhan", "cyber fraud",
        "net banking", "mobile banking",
        "बैंक", "खाता", "केवाईसी", "पिन", "లోన్", "ఖాతా", "బ్యాంక్"
    ]
    if any(kw in query_lower for kw in bank_keywords):
        return "Banking Services"
        
    # Transportation keywords (English, Hindi, Telugu)
    trans_keywords = [
        "train", "irctc", "railway", "tatkal", "bus pass", "bus", "metro",
        "ncmc", "pnr", "ticket", "reservation", "sleeper", "coach", "depot",
        "smart card", "tsrtc", "apsrtc", "dtc", "bmtc", "msrtc",
        "ट्रेन", "रेलवे", "तत्काल", "बस पास", "मेट्रो", "రైలు", "తత్కాల్", "బస్సు పాస్", "మెట్రో"
    ]
    if any(kw in query_lower for kw in trans_keywords):
        return "Public Transportation"
        
    # Government services keywords (English, Hindi, Telugu)
    gov_keywords = [
        "certificate", "income certificate", "caste certificate", "domicile",
        "residence certificate", "digilocker", "birth certificate", "death certificate",
        "ration card", "aadhaar", "pan card", "serviceplus", "meeseva", "edistrict",
        "tahsildar", "sdm", "government scheme", "scholarship", "portal",
        "प्रमाण पत्र", "आय प्रमाण पत्र", "जाति प्रमाण पत्र", "डिजिलॉकर", "जन्म प्रमाण", "ధృవీకరణ", "సర్టిఫికెట్", "డిజిలాకర్", "ఆదాయ"
    ]
    if any(kw in query_lower for kw in gov_keywords):
        return "Government Services"
        
    return None
