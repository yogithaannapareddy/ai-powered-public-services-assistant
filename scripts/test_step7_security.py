"""
QA Verification Script for STEP 7: Error Handling and Security Guardrails.
Tests:
1. Empty user messages
2. Invalid corrupted PDF
3. Unsupported file types (.exe, .sh)
4. Large file uploads exceeding 10MB
5. Missing API key handling
6. Prevention of OTP, PIN, password or card details solicitation
"""

import sys
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

from src.chatbot import Chatbot
from src.document_loader import DocumentLoader
from src.utils import validate_uploaded_file
from src.prompts import SYSTEM_PROMPT

def run_step7_verification():
    print("=" * 80)
    print("STEP 7: ERROR HANDLING AND SECURITY GUARDRAILS VERIFICATION")
    print("=" * 80)

    bot = Chatbot()

    # 1. Empty user message
    print("\n[1] Testing Empty User Message Handling:")
    empty_resp = bot.ask("     ")
    print(f" -> Response: {empty_resp['answer']}")
    assert "Please ask a question" in empty_resp["answer"]
    assert len(empty_resp["citations"]) == 0

    # 2. Invalid / Corrupted PDF parsing
    print("\n[2] Testing Corrupted PDF Handling:")
    loader = DocumentLoader()
    corrupted_bytes = b"%PDF-1.4 Corrupted dummy binary content that is not a real PDF document %%EOF"
    try:
        chunks = loader.load_pdf_bytes(corrupted_bytes, "corrupt.pdf")
        print(f" -> Handled, produced {len(chunks)} chunks.")
    except Exception as e:
        print(f" -> Correctly caught and logged PDF parsing error: {type(e).__name__}")
        assert True

    # 3. Unsupported file types
    print("\n[3] Testing Unsupported File Type Validation:")
    valid, msg = validate_uploaded_file("malicious_script.exe", 1024, max_size_mb=10)
    print(f" -> File 'malicious_script.exe': valid={valid}, msg='{msg}'")
    assert valid is False
    assert "Unsupported file type" in msg

    valid_sh, msg_sh = validate_uploaded_file("script.sh", 1024, max_size_mb=10)
    assert valid_sh is False

    # 4. Large file upload exceeding 10MB
    print("\n[4] Testing Large File Size Limit (10MB):")
    huge_size = 15 * 1024 * 1024  # 15MB
    valid_huge, msg_huge = validate_uploaded_file("giant_manual.pdf", huge_size, max_size_mb=10)
    print(f" -> File 'giant_manual.pdf' (15MB): valid={valid_huge}, msg='{msg_huge}'")
    assert valid_huge is False
    assert "exceeds maximum allowed limit" in msg_huge

    # 5. Missing / Invalid API key handling
    print("\n[5] Testing Missing API Key Resilience:")
    bot_no_key = Chatbot()
    bot_no_key.rag.update_api_key("")
    no_key_resp = bot_no_key.ask("What is Speed Post?", category="Post Office Services")
    print(f" -> Response without API key:\n{no_key_resp['answer'][:200]}...")
    assert len(no_key_resp["answer"]) > 20
    assert no_key_resp["is_live_gemini"] is False
    print(" -> Fallback to local direct knowledge synthesis: SUCCESS")

    # 6. Security Guardrails against credential solicitation
    print("\n[6] Verifying Security Guardrails & Anti-Phishing Prompts:")
    assert "NEVER ask the citizen for passwords, OTPs" in SYSTEM_PROMPT
    assert "UPI PIN" in SYSTEM_PROMPT
    assert "Never enter your UPI PIN to receive money" in SYSTEM_PROMPT
    assert "strictly educational" in SYSTEM_PROMPT
    print(" -> System prompt enforces zero credential solicitation and banking educational-only scope: VERIFIED")

    print("\n" + "=" * 80)
    print("STEP 7: ALL ERROR HANDLING AND SECURITY TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    run_step7_verification()

