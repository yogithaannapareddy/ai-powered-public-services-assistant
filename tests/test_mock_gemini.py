"""
Automated Unit Tests with Mocks for Google Gemini API Integration.
Ensures generation and citation extraction pathways are thoroughly tested
in isolated test and CI environments without network or API quota dependencies.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.rag_pipeline import RAGPipeline
from src.chatbot import Chatbot

class MockResponse:
    def __init__(self, text: str):
        self.text = text

def test_mock_gemini_generation_success():
    """Test RAGPipeline generation when Gemini API returns a successful response."""
    rag = RAGPipeline(api_key="mock_test_key_123456789")
    
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse(
        "Here are the steps to send a Speed Post parcel in India: 1. Pack securely. 2. Visit post office."
    )
    rag._genai_client = mock_client
    
    res = rag.generate("How do I send a Speed Post parcel?", category="Post Office Services")
    
    assert res["is_live_gemini"] is True
    assert "Speed Post" in res["answer"]
    assert len(res["citations"]) >= 1
    assert res["citations"][0].category == "Post Office Services"

def test_mock_gemini_unsupported_query_handling():
    """Test RAGPipeline when Gemini reports lack of verified information."""
    rag = RAGPipeline(api_key="mock_test_key_123456789")
    
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse(
        "I do not have verified official information for this specific query. Please consult the official department portal."
    )
    rag._genai_client = mock_client
    
    res = rag.generate("What is the fee for an unlisted exotic permit?", category="All Services")
    assert "not have verified official information" in res["answer"]

def test_mock_gemini_empty_response_fallback():
    """Test RAGPipeline fallback to local synthesis when Gemini returns an empty response."""
    rag = RAGPipeline(api_key="mock_test_key_123456789")
    
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse("")
    rag._genai_client = mock_client
    
    res = rag.generate("What are KYC documents for bank?", category="Banking Services")
    # Should fall back gracefully to local knowledge base synthesis
    assert len(res["answer"]) > 10
    assert "Reserve Bank of India" in res["answer"] or "Official Information" in res["answer"]

def test_mock_chatbot_multiturn_dialogue():
    """Test Chatbot multi-turn memory integration with mocked LLM."""
    rag = RAGPipeline(api_key="mock_test_key_123456789")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        MockResponse("You can open a Post Office Savings Account at any sub-post office."),
        MockResponse("For opening a Post Office account, you need Aadhaar and PAN cards.")
    ]
    rag._genai_client = mock_client
    
    bot = Chatbot(rag_pipeline=rag)
    r1 = bot.ask("I want to open a post office savings account.", category="Post Office Services")
    assert "Post Office Savings Account" in r1["answer"]
    
    r2 = bot.ask("What documents do I need?", category="Post Office Services")
    assert "Aadhaar and PAN" in r2["answer"]
    assert len(bot.get_history()) == 4

