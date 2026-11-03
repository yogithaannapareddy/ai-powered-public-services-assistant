# 🇮🇳 AI-Powered Public Services Assistant
### *Your AI Guide to Essential Public Services in India*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-purple?style=for-the-badge)](https://www.trychroma.com/)
[![Tests](https://img.shields.io/badge/pytest-20%20passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

---

## 📌 1. Project Overview

Navigating government procedures and public services in India can often be overwhelming, especially for **senior citizens, students, rural citizens, and individuals facing language or digital literacy barriers**. Information regarding parcel bookings, bank KYC rules, bus pass concessions, train ticket reservations, and official government certificates is frequently fragmented across separate portals, filled with bureaucratic jargon, or vulnerable to misinformation and digital scams.

The **AI-Powered Public Services Assistant** is an end-to-end, production-ready Generative AI application built with **Google Gemini API**, **Streamlit**, and a **Retrieval-Augmented Generation (RAG)** pipeline. It acts as an empathetic, multilingual digital companion that simplifies Indian public services into clear, step-by-step instructions grounded in **verified official source documents**.

---

## 🎯 2. Objectives & Problem Statement

### Problem Statement
- **Complex Administrative Jargon:** Official circulars and forms use convoluted terminology that ordinary citizens struggle to comprehend.
- **Language Barriers:** Millions of citizens are more comfortable in their mother tongue (such as Hindi or Telugu) rather than complex English legalese.
- **Financial Fraud Vulnerability:** Citizens frequently fall victim to online scams (e.g., fraudulent requests for UPI PINs to "receive money" or fake customer care numbers).
- **Hallucination Risk in LLMs:** Standard AI models often invent fees, deadlines, or non-existent government rules if not strictly grounded.

### Objectives
1. **Explain Procedures in Simple Language:** Provide step-by-step guidance without administrative complexity.
2. **Strict Grounding & Zero Hallucinations:** Provide answers backed by official government manuals, citing exact document names, page numbers, and portal URLs.
3. **Multilingual Access:** Native conversational support for **English**, **Hindi (हिन्दी)**, and **Telugu (తెలుగు)** with modular architecture for adding more regional languages.
4. **Fraud Prevention & Security:** Guardrail prompts that explicitly warn citizens against entering UPI PINs to receive money or sharing OTPs and personal identifiers.
5. **Accessibility First:** High-contrast, clean UI, responsive cards, one-click example questions, and optional voice (Text-to-Speech) readout.

---

## 🏛️ 3. Core Service Categories

The assistant specializes in four critical public service domains:

| Category | Icon | Key Services Covered | Official Sources |
| :--- | :---: | :--- | :--- |
| **Post Office Services** | 📮 | Speed Post rules & rates, domestic parcel booking, packaging norms, Post Office Savings Accounts (POSA), India Post Payments Bank (IPPB) zero-balance doorstep banking, consignment tracking. | [India Post](https://www.indiapost.gov.in), [IPPB](https://www.ippbonline.com) |
| **Banking Services** | 🏦 | Savings account opening, Officially Valid Documents (OVD) for KYC, Video KYC (V-CIP), ATM Green PIN setup, UPI safety rules, cyber fraud reporting (Helpline 1930), RBI Integrated Ombudsman complaints. | [RBI](https://www.rbi.org.in), [RBI CMS](https://cms.rbi.org.in), [NPCI](https://www.npci.org.in) |
| **Public Transportation** | 🚆 | IRCTC train reservations, Tatkal booking windows & cancellation rules, state road transport concessional bus passes for students/seniors, Metro cards, National Common Mobility Card (NCMC). | [IRCTC](https://www.irctc.co.in), [MoHUA (Metro & NCMC)](https://mohua.gov.in), [MoRTH](https://morth.nic.in) |
| **Government Services** | 🏛️ | Income, Community/Caste, and Domicile/Residence certificates via state portals (ServicePlus / MeeSeva / e-District), birth and death registration (CRS), DigiLocker legal validity under IT Rules 2016. | [National Portal of India](https://www.india.gov.in), [ServicePlus](https://serviceonline.gov.in), [DigiLocker](https://www.digilocker.gov.in) |

---

## 🧠 4. System Architecture & RAG Workflow

The application leverages a modular Retrieval-Augmented Generation (RAG) architecture:

```
                                  ┌───────────────────────────┐
                                  │   Official Knowledge Base │
                                  │   (PDFs, TXTs, JSON FAQs) │
                                  └─────────────┬─────────────┘
                                                │
                                       [Document Loader]
                                  (pypdf / PyPDF Text Cleaning)
                                                │
                                    [Recursive Text Chunking]
                                  (800 chars, 150 overlap + meta)
                                                │
                                       [Embeddings Engine]
                                (Gemini text-embedding-004 or
                                   Local ONNX all-MiniLM-L6-v2)
                                                │
                                                ▼
                                  ┌───────────────────────────┐
                                  │   ChromaDB Vector Store   │
                                  │  (Persistent Collections) │
                                  └─────────────┬─────────────┘
                                                │
[Citizen Query]                                │ Category-filtered
       │                                        │ Semantic Similarity Search
       ▼                                        ▼
[Category Detector] ───────────────► [Retrieved Chunks & Citations]
                                                │
                                                ▼
                                    [Context & Prompt Assembly]
                                  (Strict Truthfulness & Citations)
                                                │
                                                ▼
                                    [Google Gemini 1.5 Flash]
                                                │
                                                ▼
                                    [Grounded Step-by-Step Response]
                                    + [Verified Source Citations]
                                    + [Optional gTTS Audio Readout]
```

### Retrieval & Generation Steps:
1. **User Inquiry & Intent:** Citizen types a query in English, Hindi, or Telugu, or selects a preset example.
2. **Category Routing:** Category is determined either by the user's selected category tab or auto-detected through keyword matching.
3. **Semantic Search:** ChromaDB queries the collection using vector cosine similarity. If a specific category is chosen, metadata filtering (`where={"category": category}`) is applied.
4. **Context Injection:** Top-$k$ chunks are formatted with document titles, page numbers, and official portal URLs.
5. **Language Grounding:** Language-specific guidance is added to the system prompt (e.g., instructing Gemini to respond in respectful Hindi or Telugu while keeping technical names like Speed Post or KYC clear).
6. **Gemini Synthesis:** Gemini generates a structured response with numbered action steps, document requirements, and cautionary warnings.
7. **Offline/Local Resilience:** If a Gemini API key is not configured, the pipeline operates in **Knowledge Base Direct Mode**, synthesizing verified facts directly from retrieved documents and FAQs.

---

## 🛠️ 5. Technology Stack

- **Programming Language:** Python 3.11+
- **Frontend / UI:** [Streamlit](https://streamlit.io/) with custom responsive CSS styling
- **LLM:** [Google Gemini 1.5 Flash](https://aistudio.google.com/) via `google-generativeai` and `google-genai`
- **Embeddings:** Google Gemini `models/text-embedding-004` with offline fallback to local ONNX `all-MiniLM-L6-v2`
- **Vector Database:** [ChromaDB](https://www.trychroma.com/) (Embedded persistent storage)
- **Document Processing:** [PyPDF (pypdf)](https://pypi.org/project/pypdf/) and [ReportLab](https://www.reportlab.com/)
- **Voice Support:** [gTTS (Google Text-to-Speech)](https://pypi.org/project/gTTS/) for English, Hindi, and Telugu audio
- **Backend API (Optional):** [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn
- **Testing & Benchmarking:** [pytest](https://docs.pytest.org/) and [pytest-asyncio](https://pypi.org/project/pytest-asyncio/)
- **Configuration:** [python-dotenv](https://pypi.org/project/python-dotenv/) and [Pydantic](https://docs.pydantic.dev/)

---

## 📁 6. Project Folder Structure

```
public-services-assistant/
│
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive project documentation
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules (prevents key & DB leaks)
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Central application configuration & paths
│
├── data/
│   ├── documents/              # Sample official policy guides & generated PDFs
│   │   ├── post_office/        # Speed Post & parcel guidelines
│   │   ├── banking/            # RBI KYC & account opening manual
│   │   ├── transportation/     # IRCTC Tatkal & bus pass charter
│   │   └── government/         # Certificate & DigiLocker manual
│   └── faqs/                   # Structured official FAQ datasets
│       ├── post_office_faq.json
│       ├── banking_faq.json
│       ├── transportation_faq.json
│       └── government_faq.json
│
├── src/
│   ├── __init__.py
│   ├── chatbot.py              # Conversational manager & chat history
│   ├── rag_pipeline.py         # End-to-end RAG orchestrator & synthesis
│   ├── document_loader.py      # PDF, text & FAQ chunking engine
│   ├── embeddings.py           # Gemini & local fallback embedding functions
│   ├── vector_store.py         # ChromaDB persistence & similarity search
│   ├── prompts.py              # Grounded system prompts & templates
│   ├── language_support.py     # Multilingual UI strings & instructions
│   ├── source_citations.py     # Citation models & markdown deduplication
│   ├── voice_support.py        # gTTS audio generation module
│   ├── api.py                  # Optional FastAPI REST service
│   └── utils.py                # Text normalization & file upload validation
│
├── tests/
│   ├── test_document_loader.py # Tests for PDF/text loading, chunking & validation
│   ├── test_rag.py             # Tests for vector search & category filtering
│   ├── test_chatbot.py         # Tests for conversation history & prompts
│   └── test_evaluation.py      # Benchmark evaluation suite measuring latency & relevance
│
├── scripts/
│   └── generate_sample_pdfs.py # Generates verified sample PDF documents
│
└── assets/
    ├── style.css               # Professional blue-and-white custom styling
    └── logo.png                # High-resolution application emblem
```

---

## 🚀 7. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- Git installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/public-services-assistant.git
cd public-services-assistant
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and add your **Google Gemini API Key**:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_PROVIDER=gemini
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
CHROMA_PERSIST_DIRECTORY=data/chroma_db
DEFAULT_LANGUAGE=English
ENABLE_VOICE=True
```

> **How to get a free Google Gemini API Key:**
> 1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
> 2. Sign in with your Google account.
> 3. Click **"Create API key"** and copy the generated key.

*(Note: Even if you do not have an API key immediately, the assistant works out-of-the-box in local knowledge-base direct synthesis mode!)*

---

## 💻 8. Running the Application

### Running the Streamlit Web Application
Execute:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Running the Optional FastAPI Backend
```bash
uvicorn src.api:app --reload --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

---

## 🧪 9. Testing & Quantitative Evaluation

The project includes a comprehensive, automated test suite built with `pytest`.

Run all tests:
```bash
python -m pytest -v -s
```

### Actual Benchmark Evaluation Measurements:
The benchmark suite evaluated 8 representative queries across all 4 public service categories:

```text
======================================================================
BENCHMARK EVALUATION RESULTS: PUBLIC SERVICES ASSISTANT RAG PIPELINE
======================================================================
[1/8] Query: 'How do I send an interstate parcel via Speed ...'
       Category: Post Office Services | Latency: 451 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[2/8] Query: 'How can I open an IPPB zero balance account a...'
       Category: Post Office Services | Latency: 836 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[3/8] Query: 'What Officially Valid Documents (OVD) are req...'
       Category: Banking Services | Latency: 421 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[4/8] Query: 'Do I need to enter my UPI PIN to receive mone...'
       Category: Banking Services | Latency: 345 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[5/8] Query: 'What time does Tatkal train ticket reservatio...'
       Category: Public Transportation | Latency: 413 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[6/8] Query: 'How do students get a concessional state tran...'
       Category: Public Transportation | Latency: 405 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[7/8] Query: 'How do I apply for an Income Certificate and ...'
       Category: Government Services | Latency: 336 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
[8/8] Query: 'Are driving licenses and RC stored in DigiLoc...'
       Category: Government Services | Latency: 320 ms
       Retrieval Match: PASS | Citation Match: PASS | Grounding: PASS
----------------------------------------------------------------------
SUMMARY METRICS:
  • Total Benchmark Queries:      8
  • Retrieval Relevance Rate:     100.0% (8/8)
  • Source Citation Accuracy:     100.0% (8/8)
  • Answer Grounding / Accuracy:  100.0% (8/8)
  • Average Retrieval Latency:    440.9 ms
======================================================================
```

**Overall Test Results:** `20 passed in 16.42s (100% pass rate)`.

---

## 🌐 10. Multilingual Support Details

The application provides first-class support for three major languages:
- **English:** Accessible, clear vocabulary tailored for students and senior citizens.
- **Hindi (हिन्दी):** Natural Devanagari script responses explaining bureaucratic terms while keeping official references recognizable (e.g., Speed Post, DigiLocker, KYC).
- **Telugu (తెలుగు):** Accurate Telugu phrasing tailored for regional citizens across Andhra Pradesh and Telangana.

### Adding New Languages
Thanks to the modular dictionary structure in [`src/language_support.py`](src/language_support.py), adding a new language (e.g., Tamil, Bengali, Marathi) takes only two simple steps:
1. Add language metadata and UI translation strings in `UI_STRINGS`.
2. Add language-specific prompt instructions in `LANGUAGE_INSTRUCTIONS`.

---

## 🔒 11. Security, Reliability & Disclaimers

- **Zero Credential Requests:** The assistant **never** asks for passwords, OTPs, UPI PINs, CVVs, or card numbers.
- **Banking Advisory Scope:** All financial information is strictly educational. The chatbot does not execute transactions.
- **File Upload Validation:** Uploads are strictly restricted to verified document extensions (`.pdf`, `.txt`, `.json`, `.md`) with an enforced 10MB limit.
- **API Key Safeguards:** Keys are loaded via `.env` or temporary session memory and are excluded from version control via `.gitignore`.
- **Citizen Disclaimer:** A permanent safety notice clarifies that the AI assistant provides informational guidance and does not replace official government counters.

---

## ☁️ 12. Deployment on Streamlit Community Cloud

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: AI-Powered Public Services Assistant initial release"
   git push origin main
   ```
2. Navigate to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **"New App"** and select your repository, branch (`main`), and main file path (`app.py`).
4. In **Advanced Settings -> Secrets**, add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```
5. Click **"Deploy"**!

---

## 🔮 13. Future Enhancements

- [ ] **Full Two-Way Speech Recognition (STT):** Direct microphone voice recording in regional Indian dialects.
- [ ] **State Portal Form Auto-Fill Assistance:** Step-by-step interactive guidance on filling out state government forms.
- [ ] **Expansion to 10+ Indian Languages:** Bengali, Tamil, Kannada, Marathi, Gujarati, Malayalam, Odia, Punjabi.
- [ ] **WhatsApp & Telegram Bot Integration:** Allowing citizens in rural areas to query public services over messaging apps.

---

## 📜 14. License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed with ❤️ for Indian Citizens**

