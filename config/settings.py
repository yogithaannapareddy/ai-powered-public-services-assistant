import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
FAQS_DIR = DATA_DIR / "faqs"
CHROMA_DIR = DATA_DIR / "chroma_db"
ASSETS_DIR = BASE_DIR / "assets"

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    """Application Configuration Settings"""
    
    # Gemini LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    
    # Embedding Configuration
    # Options: "gemini" (Gemini text-embedding-004) or "huggingface" / "chroma_default"
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "gemini")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = str(CHROMA_DIR)
    CHROMA_COLLECTION_NAME: str = "public_services_knowledge"
    
    # Document Processing & Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    
    # Retrieval Configuration
    TOP_K_RETRIEVAL: int = 4
    SIMILARITY_THRESHOLD: float = 0.35
    
    # Languages Supported
    SUPPORTED_LANGUAGES = {
        "English": {
            "code": "en",
            "name": "English",
            "native_name": "English",
            "voice_code": "en"
        },
        "Hindi": {
            "code": "hi",
            "name": "Hindi",
            "native_name": "हिन्दी",
            "voice_code": "hi"
        },
        "Telugu": {
            "code": "te",
            "name": "Telugu",
            "native_name": "తెలుగు",
            "voice_code": "te"
        }
    }
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "English")
    
    # Public Service Categories
    CATEGORIES = [
        "All Services",
        "Post Office Services",
        "Banking Services",
        "Public Transportation",
        "Government Services"
    ]
    
    # Official Source URL Map
    OFFICIAL_PORTALS = {
        "Post Office Services": {
            "India Post": "https://www.indiapost.gov.in",
            "IPPB": "https://www.ippbonline.com",
            "Postal Tracking": "https://www.indiapost.gov.in/VAS/Pages/CustomerSupport/Customer-Support.aspx"
        },
        "Banking Services": {
            "Reserve Bank of India": "https://www.rbi.org.in",
            "RBI CMS Ombudsman": "https://cms.rbi.org.in",
            "NPCI (UPI Safety)": "https://www.npci.org.in",
            "National Cyber Crime": "https://cybercrime.gov.in"
        },
        "Public Transportation": {
            "IRCTC Rail Connect": "https://www.irctc.co.in",
            "Indian Railways": "https://indianrailways.gov.in",
            "MoHUA (Metro & NCMC)": "https://mohua.gov.in",
            "MoRTH (State Transport)": "https://morth.nic.in"
        },
        "Government Services": {
            "National Portal of India": "https://www.india.gov.in",
            "ServicePlus Citizen Portal": "https://serviceonline.gov.in",
            "DigiLocker": "https://www.digilocker.gov.in",
            "Civil Registration (Birth/Death)": "https://crsorgi.gov.in"
        }
    }
    
    # Voice features
    ENABLE_VOICE: bool = os.getenv("ENABLE_VOICE", "True").lower() in ("true", "1", "yes")

settings = Settings()
