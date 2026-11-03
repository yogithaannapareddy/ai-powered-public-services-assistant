"""
Voice Support Module (Optional).
Provides Text-to-Speech (TTS) audio generation via gTTS for Indian languages (EN, HI, TE)
and audio utilities for Speech-to-Text integration.
"""

import io
from typing import Optional
from config.settings import settings
from src.utils import logger

# Language code mapping for gTTS
GTTS_LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te"
}

def generate_speech_audio(text: str, language: str = "English") -> Optional[bytes]:
    """
    Generate MP3 speech bytes for the given text and language using gTTS.
    Returns bytes or None if generation fails.
    """
    if not text or not settings.ENABLE_VOICE:
        return None

    try:
        from gtts import gTTS
        lang_code = GTTS_LANG_MAP.get(language, "en")
        
        # Clean markdown characters for cleaner audio
        clean_text = text.replace("*", "").replace("#", "").replace(">", "").replace("-", " ")
        # Truncate extremely long texts for quick audio response
        if len(clean_text) > 800:
            clean_text = clean_text[:800] + "... Please refer to the text response for complete details."

        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        logger.warning(f"Voice generation failed: {e}")
        return None
