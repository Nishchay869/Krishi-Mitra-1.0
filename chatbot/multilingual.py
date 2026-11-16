"""Answer in the farmer's own language using Gemini's native multilingual understanding."""
import logging
import re
from . import engine, sarvam

logger = logging.getLogger(__name__)

ROMANIZED_LEXICONS = {
    'kn-IN': {'bele', 'belege', 'gobbara', 'hakbeku', 'madbeku', 'enu', 'hege', 'yava', 'yavaga', 'rooga', 'aushadhi', 'neeru', 'bittane', 'namaskara', 'oota', 'tumba'},
    'hi-IN': {'kya', 'kaise', 'kaun', 'kitna', 'khad', 'kheti', 'bimari', 'karein', 'dalein', 'dalna', 'chahiye', 'dawai', 'lag', 'namaste', 'bhav', 'kisan', 'pani'},
    'te-IN': {'ela', 'eppudu', 'enti', 'panta', 'pantalo', 'eruvulu', 'mandu', 'purugulu', 'kottali', 'cheyali', 'namaskaram', 'vesthe'},
    'ta-IN': {'enna', 'eppadi', 'eppothu', 'uram', 'marundhu', 'sedikku', 'payir', 'podanum', 'podalam', 'vanakkam'},
    'mr-IN': {'kasa', 'kiti', 'khad', 'pik', 'sheti', 'aushadh', 'namaskar'},
}


def detect_romanized_language(text):
    """Detect Indian language written in Latin/English script via distinctive agricultural words."""
    words = set(re.findall(r'\b[a-zA-Z]{2,}\b', str(text).lower()))
    scores = {lang: len(words.intersection(lex)) for lang, lex in ROMANIZED_LEXICONS.items()}
    best_lang, best_score = max(scores.items(), key=lambda x: x[1])
    return best_lang if best_score >= 1 else None


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


def _resolve_target(message, language=None, output_language=None):
    """Return (BotReply, reply_text_in_user_language, language_code, english_query).
    
    Optimized for strict language fidelity:
    - Non-ASCII Indian scripts (Kannada, Telugu, Tamil, Bengali, Hindi) detected instantly (<0.001ms)
    - Romanized regional words (e.g. 'ragi bele ge yava gobbara') detected via lexicon
    - User's active language always takes precedence over foreign defaults
    - Gemini instructed with strict language requirement
    """
    message_str = str(message or '').strip()
    detected_lang = None

    if not language:
        script_lang = detect_script_language(message_str)
        if script_lang:
            detected_lang = script_lang
        else:
            roman_lang = detect_romanized_language(message_str)
            if roman_lang:
                detected_lang = roman_lang
            elif message_str.isascii():
                # ASCII text without regional words -> English
                detected_lang = sarvam.ENGLISH
            elif sarvam.is_configured():
                try:
                    detected_lang = sarvam.detect_language(message_str)
                except Exception:
                    detected_lang = sarvam.ENGLISH
            else:
                detected_lang = sarvam.ENGLISH
        language = detected_lang

    # Priority rule: If the user's message is detected in a specific Indian language (script or romanized),
    # ALWAYS respect that language! Do NOT override it with Hindi or English.
    if detected_lang and detected_lang != sarvam.ENGLISH:
        target = detected_lang
    else:
        target = output_language or language or sarvam.ENGLISH
    return message_str, detected_lang, target


def _localize(reply, text, target, detected_lang):
    """Translate an English reply into the user's language when needed (Sarvam)."""

    # If the response is in English but user asked in regional language:
    if target != sarvam.ENGLISH and not any(ord(ch) > 127 for ch in text):
        translated = False
        if sarvam.is_configured():
            try:
                text = sarvam.translate(text, sarvam.ENGLISH, target)
                translated = True
            except sarvam.SarvamError:
                translated = False
        if not translated:
            if detected_lang and detected_lang != sarvam.ENGLISH:
                localized = engine.get_localized_fallback(target)
                if text == engine.FALLBACK_REPLY or reply.intent == 'general':
                    text = localized
            else:
                target = sarvam.ENGLISH

    return text, target


def respond(message, language=None, output_language=None, history=None):
    """Return (BotReply, reply_text_in_user_language, language_code, english_query).

    Optimized for strict language fidelity:
    - Non-ASCII Indian scripts (Kannada, Telugu, Tamil, Bengali, Hindi) detected instantly (<0.001ms)
    - Romanized regional words (e.g. 'ragi bele ge yava gobbara') detected via lexicon
    - User's active language always takes precedence over foreign defaults
    - Gemini instructed with strict language requirement
    """
    message_str, detected_lang, target = _resolve_target(message, language, output_language)
    reply = engine.answer(message_str, language=target, history=history)
    text, target = _localize(reply, reply.text, target, detected_lang)
    return reply, text, target, message_str


def respond_stream(message, language=None, output_language=None, history=None):
    """Streaming respond(): yields ('delta', text_piece) while the answer is written, then
    ('final', (BotReply, reply_text_in_user_language, language_code, english_query)).

    If the reply had to be translated afterwards, the final text differs from the streamed
    pieces and the client should replace what it showed.
    """
    message_str, detected_lang, target = _resolve_target(message, language, output_language)
    pieces = engine.stream_answer(message_str, language=target, history=history)
    while True:
        try:
            yield ('delta', next(pieces))
        except StopIteration as done:
            reply = done.value
            break
    text, target = _localize(reply, reply.text, target, detected_lang)
    yield ('final', (reply, text, target, message_str))
