"""Text translation and language detection: Google Gemini first, Sarvam AI as backup.

Same interface as the old Sarvam calls (translate / detect_language / is_configured), so chat,
greetings and community posts all use it. Voice (speech-to-text, text-to-speech) stays on Sarvam.
Results are cached, so the same text does not use the Gemini quota twice.
"""
import hashlib
import logging

import requests
from django.conf import settings
from django.core.cache import cache

from . import sarvam

logger = logging.getLogger(__name__)

ENGLISH = sarvam.ENGLISH
LANGUAGES = sarvam.LANGUAGES  # {'kn-IN': 'ಕನ್ನಡ', ...} languages offered in the app
GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
CACHE_SECONDS = 7 * 24 * 60 * 60

TRANSLATE_INSTRUCTION = (
    'You translate farming advice for Indian farmers. Translate the user\'s text from {source} '
    'to {target}. Keep the meaning exact. Keep numbers, units, doses, product names, chemical '
    'names, web addresses and Markdown formatting (**, lists, line breaks) unchanged. Use simple, '
    'everyday words a farmer uses. Reply with the translation only - no notes, no quotes.'
)
DETECT_INSTRUCTION = (
    'Identify the language of the user\'s text (it may be typed in its own script or in Latin '
    'letters). Reply with exactly one code from this list and nothing else: {codes}. '
    'If the text is English or you are unsure, reply {english}.'
)


class TranslationError(sarvam.SarvamError):
    """Neither Gemini nor Sarvam could translate (callers already handle SarvamError)."""


def _gemini_key():
    return getattr(settings, 'GEMINI_API_KEY', '')


def is_configured():
    return bool(_gemini_key()) or sarvam.is_configured()


def _name(code):
    return f"{LANGUAGES.get(code, code)} ({code})"


def _ask_gemini(instruction, text, max_tokens):
    model = getattr(settings, 'GEMINI_CHAT_MODEL', 'gemini-3.5-flash-lite')
    try:
        resp = requests.post(
            GEMINI_ENDPOINT.format(model=model), params={'key': _gemini_key()}, timeout=(3, 20),
            json={'system_instruction': {'parts': [{'text': instruction}]},
                  'contents': [{'role': 'user', 'parts': [{'text': text}]}],
                  'generationConfig': {'temperature': 0.2, 'maxOutputTokens': max_tokens}})
        resp.raise_for_status()
        parts = resp.json()['candidates'][0]['content']['parts']
        answer = ''.join(p.get('text', '') for p in parts if isinstance(p, dict) and not p.get('thought')).strip()
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        # Never log the exception text: the request URL contains the API key.
        raise TranslationError(f'Gemini request failed ({type(exc).__name__})') from None
    if not answer:
        raise TranslationError('Gemini returned no text')
    return answer


def translate(text, source, target, kind='answer'):
    """Translate text between BCP-47 codes such as 'en-IN' and 'kn-IN'."""
    if source == target or not text.strip():
        return text
    key = 'tr:v1:' + hashlib.sha256(f'{source}|{target}|{text}'.encode()).hexdigest()
    if (cached := cache.get(key)) is not None:
        return cached
    if _gemini_key():
        try:
            result = _ask_gemini(TRANSLATE_INSTRUCTION.format(source=_name(source), target=_name(target)),
                                 text, max_tokens=min(4096, 256 + len(text)))
            if target != ENGLISH and result.strip() == text.strip():
                raise TranslationError('Gemini returned the text untranslated')
            cache.set(key, result, CACHE_SECONDS)
            return result
        except TranslationError as exc:
            logger.warning('Gemini translation %s->%s failed: %s; trying Sarvam', source, target, exc)
    if sarvam.is_configured():
        return sarvam.translate(text, source, target, kind)   # raises SarvamError (e.g. no credits)
    raise TranslationError('No translation service available')


def detect_language(text):
    """BCP-47 code of the text, e.g. 'kn-IN' (English when unsupported or unsure)."""
    if _gemini_key():
        try:
            codes = ', '.join(sorted(LANGUAGES))
            code = _ask_gemini(DETECT_INSTRUCTION.format(codes=codes, english=ENGLISH), text[:1000], max_tokens=10)
            code = code.strip().strip('.').strip('`')
            return code if code in LANGUAGES else ENGLISH
        except TranslationError as exc:
            logger.warning('Gemini language detection failed: %s; trying Sarvam', exc)
    if sarvam.is_configured():
        return sarvam.detect_language(text)
    return ENGLISH
