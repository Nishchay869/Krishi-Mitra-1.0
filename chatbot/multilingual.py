"""Answer in the farmer's own language using Gemini's native multilingual understanding."""
import logging
from . import engine, sarvam

logger = logging.getLogger(__name__)


def detect_script_language(text):
    """Fast, zero-latency detection of Indian scripts from Unicode blocks."""
    for ch in text:
        cp = ord(ch)
        if 0x0C80 <= cp <= 0x0CFF:
            return 'kn-IN'
        if 0x0900 <= cp <= 0x097F:
            return 'hi-IN'
        if 0x0C00 <= cp <= 0x0C7F:
            return 'te-IN'
        if 0x0B80 <= cp <= 0x0BFF:
            return 'ta-IN'
        if 0x0980 <= cp <= 0x09FF:
            return 'bn-IN'
        if 0x0A80 <= cp <= 0x0AFF:
            return 'gu-IN'
        if 0x0D00 <= cp <= 0x0D7F:
            return 'ml-IN'
        if 0x0A00 <= cp <= 0x0A7F:
            return 'pa-IN'
    return None


def respond(message, language=None, output_language=None):
    """Return (BotReply, reply_text_in_user_language, language_code, english_query).
    
    Optimized for zero-latency responses:
    - Non-ASCII Indian scripts detected instantly via Unicode blocks (<0.001ms)
    - ASCII English text detected locally (<0.001ms) without blocking on remote HTTP LID
    - Gemini natively understands multilingual and Romanized queries directly
    """
    message_str = str(message or '').strip()
    if not language:
        script_lang = detect_script_language(message_str)
        if script_lang:
            language = script_lang
        elif message_str.isascii():
            # Standard ASCII English: zero network latency
            language = output_language or sarvam.ENGLISH
        elif sarvam.is_configured():
            try:
                language = sarvam.detect_language(message_str)
            except Exception:
                language = output_language or sarvam.ENGLISH
        else:
            language = output_language or sarvam.ENGLISH

    target = output_language or language or sarvam.ENGLISH
    reply = engine.answer(message_str, language=target)
    text = reply.text

    if target != sarvam.ENGLISH and not any(ord(ch) > 127 for ch in text):
        translated = False
        if sarvam.is_configured():
            try:
                text = sarvam.translate(text, sarvam.ENGLISH, target)
                translated = True
            except sarvam.SarvamError:
                translated = False
        if not translated:
            target = sarvam.ENGLISH

    return reply, text, target, message_str

