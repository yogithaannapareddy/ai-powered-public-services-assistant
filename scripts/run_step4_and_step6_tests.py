"""
Comprehensive QA Test Suite for STEP 4 (GenAI Chatbot) and STEP 6 (Multilingual Support).
Tests all exact queries required by the user against the live Gemini integration and RAG pipeline.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.chatbot import Chatbot

def run_tests():
    bot = Chatbot()
    print("=" * 80)
    print("STEP 4: TESTING GENAI CHATBOT CORE QUERIES")
    print("=" * 80)

    # 1. General conversation
    q1 = "Hello, how can you help me?"
    print(f"\n--- [Test 1: General Greeting] ---")
    print(f"Citizen: {q1}")
    res1 = bot.ask(q1)
    ans1 = res1["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res1['is_live_gemini'] else 'LOCAL'}):\n{ans1}\n")
    assert any(term in ans1.lower() for term in ["public service", "help", "guide", "post", "bank", "transport", "certificate", "सहायक"]), "Should introduce capabilities"

    # 2. Post office
    q2 = "I want to send a parcel to another state. What is the procedure?"
    print(f"\n--- [Test 2: Post Office Parcel] ---")
    print(f"Citizen: {q2}")
    res2 = bot.ask(q2, category="Post Office Services")
    ans2 = res2["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res2['is_live_gemini'] else 'LOCAL'}):\n{ans2}\n")
    print(f"Citations ({len(res2['citations'])}): {[c.source_title for c in res2['citations']]}")
    assert len(res2["citations"]) >= 1, "Should have citations"
    assert any(term in ans2.lower() for term in ["parcel", "speed post", "pack", "weight", "receipt"]), "Should contain procedural parcel steps"

    # 3. Banking
    q3 = "What documents are generally required to open a bank savings account?"
    print(f"\n--- [Test 3: Banking Account Opening & KYC] ---")
    print(f"Citizen: {q3}")
    res3 = bot.ask(q3, category="Banking Services")
    ans3 = res3["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res3['is_live_gemini'] else 'LOCAL'}):\n{ans3}\n")
    print(f"Citations ({len(res3['citations'])}): {[c.source_title for c in res3['citations']]}")
    assert any(term in ans3.lower() for term in ["aadhaar", "pan", "kyc", "bank"]), "Should provide KYC guidance"

    # 4. Public transportation
    q4 = "How can I apply for a bus pass?"
    print(f"\n--- [Test 4: Public Transport Bus Pass] ---")
    print(f"Citizen: {q4}")
    res4 = bot.ask(q4, category="Public Transportation")
    ans4 = res4["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res4['is_live_gemini'] else 'LOCAL'}):\n{ans4}\n")
    assert any(term in ans4.lower() for term in ["state", "city", "student", "pass", "depot", "transport"]), "Should provide bus pass guidance"

    # 5. Government services
    q5 = "How can I apply for a government certificate?"
    print(f"\n--- [Test 5: Government Certificates] ---")
    print(f"Citizen: {q5}")
    res5 = bot.ask(q5, category="Government Services")
    ans5 = res5["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res5['is_live_gemini'] else 'LOCAL'}):\n{ans5}\n")
    assert any(term in ans5.lower() for term in ["certificate", "state", "income", "caste", "serviceplus", "portal"]), "Should mention specific certificates and state portals"

    # 6. Unsupported information (Anti-Hallucination)
    q6 = "What is the exact current fee for an international scuba diving commercial permit in Lakshadweep?"
    print(f"\n--- [Test 6: Unsupported Information Guardrail] ---")
    print(f"Citizen: {q6}")
    res6 = bot.ask(q6, category="All Services")
    ans6 = res6["answer"]
    print(f"Assistant ({'LIVE GEMINI' if res6['is_live_gemini'] else 'LOCAL'}):\n{ans6}\n")
    assert any(term in ans6.lower() for term in ["cannot be verified", "not have verified", "not contain", "official portal", "please check", "not available", "could not find"]), "Must not invent fees; should state unverified"

    # 7. Follow-up conversation
    bot_followup = Chatbot()
    q7_a = "I want to open a post office savings account."
    print(f"\n--- [Test 7: Multi-turn Follow-up] ---")
    print(f"Citizen (Turn 1): {q7_a}")
    res7_a = bot_followup.ask(q7_a, category="Post Office Services")
    print(f"Assistant (Turn 1):\n{res7_a['answer'][:250]}...\n")

    q7_b = "What documents do I need?"
    print(f"Citizen (Turn 2): {q7_b}")
    res7_b = bot_followup.ask(q7_b, category="Post Office Services")
    ans7_b = res7_b["answer"]
    print(f"Assistant (Turn 2):\n{ans7_b}\n")
    assert any(term in ans7_b.lower() for term in ["aadhaar", "pan", "photo", "account", "post office"]), "Turn 2 should retain post office savings account context"

    print("\n" + "=" * 80)
    print("STEP 6: TESTING MULTILINGUAL SUPPORT (EN, HI, TE)")
    print("=" * 80)

    # Multilingual: English
    q_en = "How can I send a parcel through India Post?"
    print(f"\n--- [Language: English] ---")
    print(f"Citizen: {q_en}")
    res_en = bot.ask(q_en, category="Post Office Services", language="English")
    print(f"Assistant (English):\n{res_en['answer'][:300]}...\n")

    # Multilingual: Hindi
    q_hi = "मुझे डाकघर से पार्सल भेजना है। प्रक्रिया क्या है?"
    print(f"\n--- [Language: Hindi] ---")
    print(f"Citizen: {q_hi}")
    res_hi = bot.ask(q_hi, category="Post Office Services", language="Hindi")
    ans_hi = res_hi["answer"]
    print(f"Assistant (Hindi):\n{ans_hi}\n")
    assert any(term in ans_hi for term in ["डाकघर", "पार्सल", "स्पीड पोस्ट", "वजन", "रसीद"]), "Hindi response must contain Devanagari script and postal terms"

    # Multilingual: Telugu
    q_te = "పోస్ట్ ఆఫీస్ ద్వారా పార్సెల్ పంపాలంటే ఏమి చేయాలి?"
    print(f"\n--- [Language: Telugu] ---")
    print(f"Citizen: {q_te}")
    res_te = bot.ask(q_te, category="Post Office Services", language="Telugu")
    ans_te = res_te["answer"]
    print(f"Assistant (Telugu):\n{ans_te}\n")
    assert any(term in ans_te for term in ["పోస్ట్", "పార్శిల్", "పార్సెల్", "స్పీడ్", "రసీదు", "ఆఫీస్", "సమాచారం"]), "Telugu response must contain Telugu script and postal terms"

    print("\n" + "=" * 80)
    print("ALL STEP 4 AND STEP 6 QA TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
