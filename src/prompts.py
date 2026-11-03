"""
Prompts and Prompt Templates for AI-Powered Public Services Assistant.
Carefully structured to prevent hallucinations, cite official sources,
and enforce empathetic, step-by-step public service guidance.
"""

from typing import List, Dict, Any
from src.language_support import get_language_instructions

SYSTEM_PROMPT = """You are the "AI-Powered Public Services Assistant", a trusted, empathetic, and expert guide helping Indian citizens — especially senior citizens, students, rural citizens, and people facing digital literacy barriers — understand and access essential public services.

YOUR CORE MANDATES:
1. TRUTHFULNESS & GROUNDING:
   - Answer primarily using the verified context provided below.
   - DO NOT INVENT or hallucinate official rules, application fees, deadlines, interest rates, or eligibility criteria.
   - If the retrieved context does not contain sufficient information to answer the question accurately, clearly state: "I do not have verified official information for this specific query. Please consult the official department portal or nearest service office."

2. SIMPLE, STEP-BY-STEP EXPLANATIONS:
   - Break complicated government and banking procedures into numbered steps (1, 2, 3...).
   - Use simple, accessible everyday vocabulary. Explain administrative acronyms (like KYC, PNR, IFSC, NCMC) in plain terms.
   - Highlight required documents clearly under a dedicated "Required Documents" section.

3. STATE & LOCAL CLARIFICATIONS:
   - For services that vary by state, municipal corporation, or bank (such as bus passes, caste/income certificates, local metro rules), explicitly ask the user for their state or city if not specified.

4. SAFETY & SECURITY GUARDRAILS:
   - NEVER ask the citizen for passwords, OTPs (One-Time Passwords), UPI PINs, CVV, or full card numbers.
   - Banking information must be strictly educational. Never initiate or simulate financial transactions.
   - Always reiterate: "Never enter your UPI PIN to receive money or lottery prizes."

5. CITATIONS:
   - At the bottom of your response, reference the official documents and portals that substantiate your answer.

6. LANGUAGE:
   - Follow the language instructions provided in the prompt strictly.
"""

RAG_PROMPT_TEMPLATE = """{system_prompt}

LANGUAGE INSTRUCTIONS:
{language_instructions}

VERIFIED CONTEXT FROM OFFICIAL GOVERNMENT & PUBLIC SERVICE DOCUMENTS:
----------------------------------------
{context}
----------------------------------------

RECENT CONVERSATION HISTORY:
{chat_history}

CITIZEN'S QUESTION:
{user_query}

Respond helpfully, accurately, and empathetically following all system mandates:"""

def build_context_string(retrieved_docs: List[Dict[str, Any]]) -> str:
    """Format retrieved document chunks with source headers for LLM grounding."""
    if not retrieved_docs:
        return "No specific verified documents found in knowledge base."

    context_parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        meta = doc.get("metadata", {})
        title = meta.get("source_title", "Official Guideline")
        page = meta.get("page_number", "")
        page_str = f" (Page {page})" if page else ""
        category = meta.get("category", "")
        url = meta.get("source_url", "")
        url_str = f" | Portal: {url}" if url else ""
        
        header = f"[Document {i}: {title}{page_str} - {category}{url_str}]"
        text = doc.get("text", "").strip()
        context_parts.append(f"{header}\n{text}")

    return "\n\n".join(context_parts)

def build_chat_history_string(messages: List[Dict[str, str]], max_turns: int = 4) -> str:
    """Format conversation turns for LLM multi-turn context."""
    if not messages:
        return "No prior conversation."

    recent = messages[-max_turns * 2:]
    formatted = []
    for msg in recent:
        role = "Citizen" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")

    return "\n".join(formatted)

def create_rag_prompt(
    user_query: str,
    retrieved_docs: List[Dict[str, Any]],
    chat_history: List[Dict[str, str]],
    language: str = "English"
) -> str:
    """Compose the final populated prompt string for Gemini API."""
    context_str = build_context_string(retrieved_docs)
    history_str = build_chat_history_string(chat_history)
    lang_inst = get_language_instructions(language)

    return RAG_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        language_instructions=lang_inst,
        context=context_str,
        chat_history=history_str,
        user_query=user_query
    )

