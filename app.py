"""
AI-Powered Public Services Assistant
Main Streamlit Application
A conversational AI guide for Indian public services:
Post Office, Banking, Public Transportation, and Government Services.
"""

import os
from pathlib import Path
import streamlit as st

from config.settings import settings, BASE_DIR, ASSETS_DIR
from src.chatbot import Chatbot
from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore
from src.document_loader import DocumentLoader
from src.language_support import get_text, get_example_questions
from src.source_citations import SourceCitation, format_citations_markdown
from src.voice_support import generate_speech_audio
from src.utils import validate_uploaded_file, logger

# Page configuration
st.set_page_config(
    page_title="AI-Powered Public Services Assistant",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_file = ASSETS_DIR / "style.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Helper function to initialize vector store and index documents if empty
@st.cache_resource(show_spinner=False)
def initialize_system(api_key: str):
    """Initialize vector store and auto-index initial documents if empty."""
    vs = VectorStore(api_key=api_key)
    doc_count = vs.count()
    if doc_count == 0:
        logger.info("Vector store is empty. Ingesting default sample knowledge base...")
        loader = DocumentLoader(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        chunks = loader.load_all_sample_knowledge()
        if chunks:
            vs.add_chunks(chunks)
            logger.info(f"Indexed {len(chunks)} chunks into vector store.")
    rag = RAGPipeline(vector_store=vs, api_key=api_key)
    bot = Chatbot(rag_pipeline=rag)
    return vs, rag, bot

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All Services"
if "selected_language" not in st.session_state:
    st.session_state.selected_language = settings.DEFAULT_LANGUAGE
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = settings.GEMINI_API_KEY
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Get components
vs, rag, bot = initialize_system(st.session_state.gemini_api_key)

# Sync dynamic API key changes
if st.session_state.gemini_api_key != rag.api_key:
    rag.update_api_key(st.session_state.gemini_api_key)

lang = st.session_state.selected_language

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=80)
    st.markdown("### 🇮🇳 Public Services Assistant")
    st.caption("AI-Powered Guide for Citizen Services in India")
    st.divider()

    # 1. Language Selector
    st.subheader(f"🌐 {get_text('select_language', lang)}")
    lang_options = list(settings.SUPPORTED_LANGUAGES.keys())
    selected_lang = st.selectbox(
        label="Language",
        options=lang_options,
        index=lang_options.index(st.session_state.selected_language),
        format_func=lambda x: f"{settings.SUPPORTED_LANGUAGES[x]['native_name']} ({x})",
        label_visibility="collapsed"
    )
    if selected_lang != st.session_state.selected_language:
        st.session_state.selected_language = selected_lang
        st.rerun()

    st.divider()

    # 2. Gemini API Key Configuration
    st.subheader("🔑 Gemini API Key")
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="Enter your Gemini API key...",
        help="Get a free key from https://aistudio.google.com/app/apikey"
    )
    if api_key_input != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key_input
        rag.update_api_key(api_key_input)
        st.rerun()

    if st.session_state.gemini_api_key:
        st.success("Gemini API Connected ✅", icon="🟢")
    else:
        st.info("Direct Knowledge-Base Mode (Add API key for full AI synthesis)", icon="ℹ️")

    st.divider()

    # 3. Knowledge Base Status & Re-index
    st.subheader("📊 Knowledge Base")
    total_chunks = vs.count()
    st.markdown(f"Indexed Chunks: **{total_chunks}**")

    if st.button("🔄 Re-index Knowledge Base", use_container_width=True):
        with st.spinner("Re-indexing official documents & FAQs..."):
            vs.reset()
            loader = DocumentLoader(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
            chunks = loader.load_all_sample_knowledge()
            vs.add_chunks(chunks)
            st.success(f"Indexed {len(chunks)} chunks!")
            st.rerun()

    st.divider()

    # 4. Upload Official Document
    st.subheader(f"📄 {get_text('upload_doc_title', lang)}")
    uploaded_file = st.file_uploader(
        label="Upload Document",
        type=["pdf", "txt", "json", "md"],
        help=get_text("upload_doc_help", lang),
        label_visibility="collapsed"
    )

    upload_category = st.selectbox(
        "Document Category",
        options=[c for c in settings.CATEGORIES if c != "All Services"],
        index=0
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        is_valid, msg = validate_uploaded_file(uploaded_file.name, len(file_bytes), settings.MAX_UPLOAD_SIZE_MB)
        if not is_valid:
            st.error(msg)
        else:
            if st.button("📥 Process & Ingest Document", use_container_width=True):
                with st.spinner("Parsing and vectorizing document..."):
                    loader = DocumentLoader()
                    if uploaded_file.name.lower().endswith(".pdf"):
                        new_chunks = loader.load_pdf_bytes(
                            file_bytes,
                            uploaded_file.name,
                            category=upload_category
                        )
                    else:
                        text_content = file_bytes.decode("utf-8", errors="ignore")
                        new_chunks = loader.chunk_text(
                            text_content,
                            base_metadata={
                                "source_title": Path(uploaded_file.name).stem.replace("_", " ").title(),
                                "file_name": uploaded_file.name,
                                "page_number": 1,
                                "category": upload_category,
                                "source_url": ""
                            }
                        )

                    if new_chunks:
                        vs.add_chunks(new_chunks)
                        st.success(f"Ingested {len(new_chunks)} chunks from '{uploaded_file.name}'!")
                        st.rerun()
                    else:
                        st.warning("No readable text found in document.")

    st.divider()

    # 5. Clear Chat
    if st.button(f"🗑️ {get_text('clear_chat', lang)}", use_container_width=True):
        st.session_state.messages = []
        bot.clear_history()
        st.rerun()

    # 6. Safety & Security Disclaimer
    st.markdown("---")
    st.warning(
        f"**{get_text('disclaimer_title', lang)}**\n\n"
        f"{get_text('disclaimer_text', lang)}",
        icon="⚠️"
    )


# ================================================================
# MAIN PAGE CONTENT
# ================================================================

# Application Header Banner
st.markdown(
    f"""
    <div class="assistant-header">
        <h1>🇮🇳 {get_text('app_title', lang)}</h1>
        <p>{get_text('tagline', lang)}</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Welcome description
st.write(f"**{get_text('welcome_header', lang)}**")
st.write(get_text("welcome_desc", lang))

# Category Filter Buttons / Navigation
st.markdown(f"#### 📂 {get_text('select_category', lang)}")
cols = st.columns(4)

categories_meta = [
    {
        "name": "Post Office Services",
        "icon": "📮",
        "label": get_text("category_po", lang),
        "desc": "Speed Post, Parcel booking, Savings accounts, IPPB doorstep banking."
    },
    {
        "name": "Banking Services",
        "icon": "🏦",
        "label": get_text("category_bank", lang),
        "desc": "Account opening, KYC verification, ATM PIN, UPI safety rules, RBI complaints."
    },
    {
        "name": "Public Transportation",
        "icon": "🚆",
        "label": get_text("category_trans", lang),
        "desc": "Train reservations, Tatkal timings, concessional bus passes, Metro & NCMC."
    },
    {
        "name": "Government Services",
        "icon": "🏛️",
        "label": get_text("category_gov", lang),
        "desc": "Income/Caste certificates, DigiLocker validity, birth & death registration."
    }
]

for idx, cat_info in enumerate(categories_meta):
    with cols[idx]:
        is_active = (st.session_state.selected_category == cat_info["name"])
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{cat_info['icon']} {cat_info['label']}", key=f"cat_btn_{idx}", type=btn_type, use_container_width=True):
            if st.session_state.selected_category == cat_info["name"]:
                st.session_state.selected_category = "All Services"
            else:
                st.session_state.selected_category = cat_info["name"]
            st.rerun()

st.caption(f"Currently active category: **{st.session_state.selected_category}**")

# Suggested Example Questions
example_qs = get_example_questions(st.session_state.selected_category, lang)
if example_qs:
    st.markdown(f"**💡 {get_text('example_questions_label', lang)}**")
    eq_cols = st.columns(len(example_qs))
    for i, eq in enumerate(example_qs):
        with eq_cols[i]:
            if st.button(eq, key=f"eq_btn_{i}", use_container_width=True):
                st.session_state.pending_query = eq
                st.rerun()

st.divider()

# ================================================================
# CHAT INTERFACE
# ================================================================

# Display existing conversation history
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🇮🇳"):
        st.markdown(msg["content"])
        
        # Display verified citations if available
        citations = msg.get("citations", [])
        if citations:
            with st.expander(f"📚 {get_text('source_citations_label', lang)} ({len(citations)})", expanded=False):
                for c in citations:
                    page_str = f" | Page: {c.page_number}" if c.page_number else ""
                    cat_str = f" | Category: {c.category}" if c.category else ""
                    url_str = f" | [Official Link]({c.source_url})" if c.source_url else ""
                    st.markdown(f"• **{c.source_title}**{page_str}{cat_str}{url_str}")
                    if c.snippet:
                        st.caption(f"Excerpt: \"{c.snippet.strip()}\"")
                        
        # Display audio player if generated
        if msg.get("audio_bytes"):
            st.audio(msg["audio_bytes"], format="audio/mp3")

# Check for pending query from example button or chat input
user_query = st.chat_input(placeholder=get_text("chat_input_placeholder", lang))

if st.session_state.pending_query:
    user_query = st.session_state.pending_query
    st.session_state.pending_query = None

if user_query:
    # 1. Render citizen query
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_query)

    # 2. Compute response
    with st.chat_message("assistant", avatar="🇮🇳"):
        with st.spinner(get_text("thinking_label", lang)):
            response_data = bot.ask(
                user_message=user_query,
                category=st.session_state.selected_category,
                language=lang
            )
            answer_text = response_data.get("answer", "")
            citations = response_data.get("citations", [])
            latency = response_data.get("latency_ms", 0)

            # Render answer
            st.markdown(answer_text)

            # Render citations
            if citations:
                with st.expander(f"📚 {get_text('source_citations_label', lang)} ({len(citations)})", expanded=True):
                    for c in citations:
                        page_str = f" | Page: {c.page_number}" if c.page_number else ""
                        cat_str = f" | Category: {c.category}" if c.category else ""
                        url_str = f" | [Official Link]({c.source_url})" if c.source_url else ""
                        st.markdown(f"• **{c.source_title}**{page_str}{cat_str}{url_str}")
                        if c.snippet:
                            st.caption(f"Excerpt: \"{c.snippet.strip()}\"")

            # Generate voice audio if enabled
            audio_bytes = None
            if settings.ENABLE_VOICE:
                try:
                    audio_bytes = generate_speech_audio(answer_text, language=lang)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    logger.warning(f"Voice playback skipped: {e}")

            st.caption(f"⏱️ Response generated in {latency} ms | Mode: {'Gemini AI' if response_data.get('is_live_gemini') else 'Knowledge Base Direct'}")

    # 3. Save to session state
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "citations": citations,
        "audio_bytes": audio_bytes
    })
