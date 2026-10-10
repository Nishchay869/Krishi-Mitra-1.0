"""Answer in the farmer's own language.

The question is translated to English, answered by the grounded retrieval engine, and the
answer translated back, so replies stay tied to the curated knowledge base (spec §4.3)
whatever language the farmer uses.
"""
import logging

from . import engine, sarvam

logger = logging.getLogger(__name__)


def respond(message, language=None):
    """Return (BotReply, reply_text_in_user_language, language_code, english_query)."""
    if not sarvam.is_configured():
        reply = engine.answer(message)
        return reply, reply.text, sarvam.ENGLISH, message

    try:
        if language is None:
            # Always detect: Sarvam also recognises romanised Hindi/Kannada typed in English letters.
            language = sarvam.detect_language(message)
        query_en = sarvam.translate(message, language, sarvam.ENGLISH, kind='query') if language != sarvam.ENGLISH else message
        reply = engine.answer(query_en)
        text = sarvam.translate(reply.text, sarvam.ENGLISH, language) if language != sarvam.ENGLISH else reply.text
        return reply, text, language, query_en
    except sarvam.SarvamError:
        logger.exception('Sarvam translation failed; answering in English')
        reply = engine.answer(message)
        return reply, reply.text, sarvam.ENGLISH, message
