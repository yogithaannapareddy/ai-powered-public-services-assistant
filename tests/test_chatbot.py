import pytest
from src.chatbot import Chatbot
from src.rag_pipeline import RAGPipeline
from src.language_support import get_text, get_language_instructions, get_example_questions
from src.prompts import create_rag_prompt

def test_language_support_strings():
    # English
    assert "AI-Powered Public Services Assistant" in get_text("app_title", "English")
    # Hindi
    assert "एआई-संचालित जन सेवा सहायक" in get_text("app_title", "Hindi")
    # Telugu
    assert "ఏఐ పబ్లిక్ సర్వీసెస్ అసిస్టెంట్" in get_text("app_title", "Telugu")

def test_example_questions_retrieval():
    en_qs = get_example_questions("Post Office Services", "English")
    assert len(en_qs) > 0
    assert any("parcel" in q.lower() for q in en_qs)

    hi_qs = get_example_questions("Banking Services", "Hindi")
    assert len(hi_qs) > 0

    te_qs = get_example_questions("Public Transportation", "Telugu")
    assert len(te_qs) > 0

def test_chatbot_conversation_flow():
    bot = Chatbot()
    assert len(bot.get_history()) == 0

    # 1. Ask initial question
    resp1 = bot.ask("I want to send a parcel to another state. What should I do?", category="Post Office Services")
    assert len(bot.get_history()) == 2
    assert bot.get_history()[0]["role"] == "user"
    assert bot.get_history()[1]["role"] == "assistant"

    # 2. Ask follow-up question
    resp2 = bot.ask("How long will it take to reach?", category="Post Office Services")
    assert len(bot.get_history()) == 4
    assert bot.get_history()[2]["role"] == "user"
    assert bot.get_history()[3]["role"] == "assistant"

    # 3. Clear chat
    bot.clear_history()
    assert len(bot.get_history()) == 0

def test_empty_query_handling():
    bot = Chatbot()
    resp = bot.ask("   ")
    assert "Please ask a question" in resp["answer"]
    assert len(bot.get_history()) == 0

def test_create_rag_prompt_structure():
    user_query = "What documents do I need for a bus pass?"
    retrieved_docs = [{
        "text": "Student bus pass requires bonafide certificate and Aadhaar card.",
        "metadata": {
            "source_title": "State Road Transport Guidelines",
            "page_number": 2,
            "category": "Public Transportation",
            "source_url": "https://morth.nic.in"
        }
    }]
    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi, how can I help?"}]

    prompt = create_rag_prompt(user_query, retrieved_docs, history, language="English")
    assert "AI-Powered Public Services Assistant" in prompt
    assert "State Road Transport Guidelines" in prompt
    assert "Page 2" in prompt
    assert user_query in prompt
    assert "NEVER ask the citizen for passwords, OTPs" in prompt
