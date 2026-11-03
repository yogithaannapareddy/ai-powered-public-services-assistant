import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY", "").strip()

print(f"API Key present: {bool(api_key)}")
print(f"Key length: {len(api_key)}")
print(f"Key prefix: {api_key[:6]}..." if len(api_key) > 6 else "Too short")

if api_key:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        print("Listing available models for this key:")
        for m in client.models.list():
            if "gemini" in m.name.lower():
                print(" -", m.name, getattr(m, "supported_actions", []))
    except Exception as e:
        print("List models error:", e)
else:
    print("No API key configured.")
