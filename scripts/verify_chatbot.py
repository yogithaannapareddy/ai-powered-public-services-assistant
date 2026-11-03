"""
End-to-End Chatbot Query Verification Script.
Simulates a citizen asking questions across all 4 categories:
Post Office, Banking, Public Transportation, and Government Services.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.chatbot import Chatbot

def run_verification():
    bot = Chatbot()

    queries = [
        ("I want to send a parcel to another state. What should I do?", "Post Office Services"),
        ("What documents are required to open a savings bank account under KYC?", "Banking Services"),
        ("What is the procedure and timing for Tatkal train booking?", "Public Transportation"),
        ("Are documents stored in DigiLocker legally valid for police verification?", "Government Services")
    ]

    print("=" * 80)
    print("END-TO-END CHATBOT CITIZEN QUERY VERIFICATION")
    print("=" * 80)

    for q, cat in queries:
        resp = bot.ask(q, category=cat)
        ans = resp["answer"][:250].replace("\n", " ")
        citations = resp["citations"]

        print(f"\n[Citizen Query]: {q}")
        print(f"[Category]: {cat}")
        print(f"[Answer Excerpt]: {ans}...")
        print(f"[Verified Citations ({len(citations)} found)]:")
        for c in citations:
            page_info = f" (Page {c.page_number})" if c.page_number else ""
            url_info = f" | Portal: {c.source_url}" if c.source_url else ""
            print(f"   • {c.source_title}{page_info}{url_info}")

        assert len(citations) >= 1, f"Expected citations for '{q}', got 0"
        assert len(resp["answer"]) > 50, f"Expected substantive answer for '{q}'"

    print("\n" + "=" * 80)
    print("Conversation History Turns in Session:", len(bot.get_history()))
    print("ALL 4 CATEGORY VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
