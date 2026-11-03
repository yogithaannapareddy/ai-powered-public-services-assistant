"""
Multilingual Support Module for AI-Powered Public Services Assistant.
Supports English, Hindi, and Telugu, designed for modular extension to other Indian languages.
"""

from typing import Dict, Any

# UI Localization Dictionary
UI_STRINGS: Dict[str, Dict[str, str]] = {
    "English": {
        "app_title": "AI-Powered Public Services Assistant",
        "tagline": "Your AI Guide to Essential Public Services",
        "welcome_header": "Welcome to Your Citizen Public Services Guide",
        "welcome_desc": (
            "Easily explore and understand Indian public services — from Speed Post and banking "
            "KYC to bus passes, railway tickets, and government certificates."
        ),
        "category_all": "All Services",
        "category_po": "Post Office Services",
        "category_bank": "Banking Services",
        "category_trans": "Public Transportation",
        "category_gov": "Government Services",
        "select_category": "Choose Service Category",
        "select_language": "Choose Language",
        "chat_input_placeholder": "Ask a question about public services in India...",
        "clear_chat": "Clear Conversation",
        "upload_doc_title": "Upload Document",
        "upload_doc_help": "Upload official PDF, TXT or JSON documents (Max 10MB)",
        "source_citations_label": "Official Verified Sources & Citations",
        "disclaimer_title": "Citizen Safety & Information Disclaimer",
        "disclaimer_text": (
            "This AI assistant provides informational guidance based on verified official guidelines. "
            "It does NOT represent a government agency or financial institution. Never share passwords, "
            "OTPs, PINs, or banking credentials."
        ),
        "listen_voice": "Listen to Answer",
        "thinking_label": "Searching official knowledge base...",
        "api_key_missing_warning": "Gemini API key is not configured. Running in local knowledge-base retrieval mode.",
        "example_questions_label": "Suggested Example Questions:"
    },
    "Hindi": {
        "app_title": "एआई-संचालित जन सेवा सहायक",
        "tagline": "आवश्यक सार्वजनिक सेवाओं के लिए आपका एआई मार्गदर्शक",
        "welcome_header": "सार्वजनिक सेवा सहायता केंद्र में आपका स्वागत है",
        "welcome_desc": (
            "डाकघर, बैंकिंग, सार्वजनिक परिवहन और सरकारी प्रमाणपत्रों से संबंधित "
            "नियमों और प्रक्रियाओं को आसान भाषा में समझें।"
        ),
        "category_all": "सभी सेवाएं",
        "category_po": "डाकघर सेवाएं",
        "category_bank": "बैंकिंग सेवाएं",
        "category_trans": "सार्वजनिक परिवहन",
        "category_gov": "सरकारी सेवाएं",
        "select_category": "सेवा श्रेणी चुनें",
        "select_language": "भाषा चुनें",
        "chat_input_placeholder": "सार्वजनिक सेवाओं से संबंधित अपना प्रश्न पूछें...",
        "clear_chat": "बातचीत साफ़ करें",
        "upload_doc_title": "दस्तावेज़ अपलोड करें",
        "upload_doc_help": "आधिकारिक PDF, TXT या JSON फ़ाइल अपलोड करें (अधिकतम 10MB)",
        "source_citations_label": "सत्यापित आधिकारिक स्रोत एवं संदर्भ",
        "disclaimer_title": "नागरिक सुरक्षा एवं सूचना अस्वीकरण",
        "disclaimer_text": (
            "यह एआई सहायक केवल सूचनात्मक मार्गदर्शन प्रदान करता है। "
            "यह किसी सरकारी विभाग या बैंक का प्रतिनिधित्व नहीं करता। "
            "कभी भी अपना ओटीपी (OTP), पिन (PIN) या पासवर्ड साझा न करें।"
        ),
        "listen_voice": "उत्तर सुनें (आवाज़ में)",
        "thinking_label": "आधिकारिक ज्ञानकोष से जानकारी खोजी जा रही है...",
        "api_key_missing_warning": "Gemini API कुंजी कॉन्फ़िगर नहीं है। स्थानीय ज्ञानकोष मोड सक्रिय है।",
        "example_questions_label": "सुझाए गए उदाहरण प्रश्न:"
    },
    "Telugu": {
        "app_title": "ఏఐ పబ్లిక్ సర్వీసెస్ అసిస్టెంట్",
        "tagline": "ప్రజా సేవల కోసం మీ ఏఐ సహాయకుడు",
        "welcome_header": "పౌర సేవల సహాయ కేంద్రానికి స్వాగతం",
        "welcome_desc": (
            "పోస్ట్ ఆఫీస్, బ్యాంకింగ్, బస్సు/రైలు ప్రయాణం, ప్రభుత్వ ధృవీకరణ పత్రాల వివరాలను "
            "సులువైన భాషలో సులభంగా తెలుసుకోండి."
        ),
        "category_all": "అన్ని సేవలు",
        "category_po": "పోస్టల్ సేవలు",
        "category_bank": "బ్యాంకింగ్ సేవలు",
        "category_trans": "ప్రజా రవాణా",
        "category_gov": "ప్రభుత్వ సేవలు",
        "select_category": "సేవా విభాగాన్ని ఎంచుకోండి",
        "select_language": "భాషను ఎంచుకోండి",
        "chat_input_placeholder": "ప్రజా సేవల గురించి మీ ప్రశ్నను అడగండి...",
        "clear_chat": "చాట్ క్లియర్ చేయండి",
        "upload_doc_title": "పత్రాన్ని అప్‌లోడ్ చేయండి",
        "upload_doc_help": "అధికారిక PDF, TXT లేదా JSON ఫైల్‌ను అప్‌లోడ్ చేయండి (గరిష్టంగా 10MB)",
        "source_citations_label": "ధృవీకరించబడిన అధికారిక ఆధారాలు",
        "disclaimer_title": "పౌర భద్రత మరియు సమాచార నిరాకరణ",
        "disclaimer_text": (
            "ఈ సహాయకుడు అధికారిక నిబంధనల ఆధారంగా మార్గదర్శకత్వాన్ని మాత్రమే అందిస్తాడు. "
            "ఇది ప్రభుత్వ సంస్థ కాదు. మీ OTP, PIN లేదా పాస్‌వర్డ్‌లను ఎవరితోనూ పంచుకోకండి."
        ),
        "listen_voice": "సమాధానం వినండి (వాయిస్)",
        "thinking_label": "అధికారిక సమాచార నిల్వ నుండి వెతుకుతోంది...",
        "api_key_missing_warning": "Gemini API కీ కాన్ఫిగర్ కాలేదు. లోకల్ నాలెడ్జ్ బేస్ మోడ్ పనిచేస్తోంది.",
        "example_questions_label": "నమూనా ప్రశ్నలు:"
    }
}

# Prompt instructions per language for Gemini
LANGUAGE_INSTRUCTIONS: Dict[str, str] = {
    "English": (
        "Respond in simple, clear, and courteous English. Use bullet points and numbered steps. "
        "Explain administrative jargon in easy-to-understand terms suitable for students and senior citizens."
    ),
    "Hindi": (
        "सरल, स्पष्ट और सम्मानजनक हिन्दी में उत्तर दें। "
        "कठिन प्रशासनिक शब्दों का सरल अर्थ समझाएं। "
        "बुलेट पॉइंट्स और क्रमबद्ध चरणों (1, 2, 3...) का उपयोग करें। "
        "महत्वपूर्ण आधिकारिक शब्दों (जैसे Speed Post, KYC, Aadhaar, DigiLocker, UPI PIN) को अंग्रेजी या कोष्ठक में भी स्पष्ट रखें ताकि नागरिक भ्रमित न हों।"
    ),
    "Telugu": (
        "సరళమైన, స్పష్టమైన మరియు గౌరవప్రదమైన తెలుగులో సమాధానం ఇవ్వండి. "
        "స్టెప్ బై స్టెప్ (1, 2, 3...) నంబర్లతో వివరించండి. "
        "ప్రజలకు సులభంగా అర్థమయ్యే పదజాలం ఉపయోగించండి. "
        "ముఖ్యమైన అధికారిక పేర్లు (Speed Post, KYC, Aadhaar, DigiLocker, UPI PIN మొదలైనవి) అవసరమైన చోట ఆంగ్లంలో లేదా బ్రాకెట్లలో ఉంచండి."
    )
}

# Example questions per category and language
EXAMPLE_QUESTIONS: Dict[str, Dict[str, list]] = {
    "English": {
        "Post Office Services": [
            "I want to send a parcel to another state. What should I do?",
            "How do I track my Speed Post parcel?",
            "How do I open an IPPB zero balance account at my doorstep?"
        ],
        "Banking Services": [
            "What documents are needed to open a savings bank account?",
            "What are the safety rules for UPI payments?",
            "How do I file a complaint with the RBI Ombudsman?"
        ],
        "Public Transportation": [
            "What is the Tatkal train ticket booking procedure and timing?",
            "How can students apply for a concessional bus pass?",
            "What is the National Common Mobility Card (NCMC)?"
        ],
        "Government Services": [
            "How do I apply for an Income or Caste Certificate?",
            "Are DigiLocker documents legally valid for traffic police?",
            "What is the procedure to get a birth certificate?"
        ]
    },
    "Hindi": {
        "Post Office Services": [
            "मुझे दूसरे राज्य में पार्सल भेजना है, मुझे क्या करना चाहिए?",
            "मैं अपने स्पीड पोस्ट पार्सल को कैसे ट्रैक कर सकता हूँ?",
            "डाकघर में घर बैठे IPPB खाता कैसे खुलवाएं?"
        ],
        "Banking Services": [
            "नया बैंक खाता खोलने के लिए कौन-से दस्तावेज़ आवश्यक हैं?",
            "UPI पेमेंट करते समय कौन-सी सुरक्षा सावधानियां बरतनी चाहिए?",
            "आरबीआई लोकपाल (Ombudsman) के पास शिकायत कैसे दर्ज करें?"
        ],
        "Public Transportation": [
            "IRCTC पर तत्काल ट्रेन टिकट बुकिंग का समय और नियम क्या हैं?",
            "छात्र रियायती बस पास के लिए कैसे आवेदन करें?",
            "नेशनल कॉमन मोबिलिटी कार्ड (NCMC) क्या है?"
        ],
        "Government Services": [
            "आय या जाति प्रमाण पत्र के लिए कैसे आवेदन करें?",
            "क्या डिजिलॉकर (DigiLocker) के दस्तावेज़ कानूनी रूप से मान्य हैं?",
            "जन्म प्रमाण पत्र प्राप्त करने की प्रक्रिया क्या है?"
        ]
    },
    "Telugu": {
        "Post Office Services": [
            "నేను వేరే రాష్ట్రానికి పార్శిల్‌ పంపాలనుకుంటున్నాను, ఏమి చేయాలి?",
            "నా స్పీడ్ పోస్ట్ పార్శిల్‌ను ఎలా ట్రాక్ చేయాలి?",
            "ఇంటి వద్దే IPPB జీరో బ్యాలెన్స్ ఖాతా ఎలా తెరవాలి?"
        ],
        "Banking Services": [
            "కొత్త బ్యాంక్ ఖాతా తెరవడానికి ఏ డాక్యుమెంట్లు అవసరం?",
            "UPI చెల్లింపుల సమయంలో పాటించాల్సిన భద్రతా నియమాలు ఏమిటి?",
            "బ్యాంకు సమస్యలపై RBI అంబుడ్స్‌మన్‌కు ఎలా ఫిర్యాదు చేయాలి?"
        ],
        "Public Transportation": [
            "రైలు తత్కాల్ టికెట్ బుకింగ్ సమయాలు మరియు నియమాలు ఏమిటి?",
            "విద్యార్థులు రాయితీ బస్సు పాస్ కోసం ఎలా దరఖాస్తు చేసుకోవాలి?",
            "నేషనల్ కామన్ మొబిలిటీ కార్డ్ (NCMC) అంటే ఏమిటి?"
        ],
        "Government Services": [
            "ఆదాయ లేదా కుల ధృవీకరణ పత్రం (సర్టిఫికెట్) కోసం ఎలా దరఖాస్తు చేయాలి?",
            "డిజిలాకర్ (DigiLocker) డాక్యుమెంట్లు చట్టబద్ధంగా చెల్లుబాటు అవుతాయా?",
            "పుట్టిన తేదీ ధృవీకరణ పత్రం (Birth Certificate) ఎలా పొందాలి?"
        ]
    }
}

def get_text(key: str, language: str = "English") -> str:
    """Retrieve localized UI text with fallback to English."""
    lang_dict = UI_STRINGS.get(language, UI_STRINGS["English"])
    return lang_dict.get(key, UI_STRINGS["English"].get(key, key))

def get_language_instructions(language: str = "English") -> str:
    """Get system prompt guidance for the chosen language."""
    return LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])

def get_example_questions(category: str, language: str = "English") -> list:
    """Get suggested questions for the given category and language."""
    lang_examples = EXAMPLE_QUESTIONS.get(language, EXAMPLE_QUESTIONS["English"])
    if category in lang_examples:
        return lang_examples[category]
    # If "All Services", aggregate one from each category
    all_examples = []
    for cat, qs in lang_examples.items():
        if qs:
            all_examples.append(qs[0])
    return all_examples
