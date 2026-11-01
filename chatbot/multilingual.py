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
    """Return (BotReply, reply_text_in_user_language, language_code, english_query)."""
    if not language:
        script_lang = detect_script_language(message)
        if script_lang:
            language = script_lang
        elif sarvam.is_configured():
            try:
                language = sarvam.detect_language(message)
            except Exception:
                language = output_language or sarvam.ENGLISH
        else:
            language = output_language or sarvam.ENGLISH

    target = output_language or language or sarvam.ENGLISH
    reply = engine.answer(message, language=target)
    text = reply.text

    if sarvam.is_configured() and target != sarvam.ENGLISH and not any(ord(ch) > 127 for ch in text):
        try:
            text = sarvam.translate(text, sarvam.ENGLISH, target)
        except sarvam.SarvamError:
            pass

    return reply, text, target, message
