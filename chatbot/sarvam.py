"""Sarvam AI client: language detection, translation and speech-to-text for Indian languages.

Docs: https://docs.sarvam.ai/api-reference-docs
"""
import hashlib

import requests
from django.conf import settings
from django.core.cache import cache

API_BASE = 'https://api.sarvam.ai'
# mayura handles short, colloquial and romanised questions ("gehu me kitna khad") cleanly;
# sarvam-translate takes longer text, so it is used for knowledge-base answers.
QUERY_MODEL, QUERY_MAX_CHARS = 'mayura:v1', 1000
ANSWER_MODEL, ANSWER_MAX_CHARS = 'sarvam-translate:v1', 2000
STT_MODEL = 'saaras:v4'
TRANSLATION_CACHE_SECONDS = 7 * 24 * 60 * 60

ENGLISH = 'en-IN'
LANGUAGES = {
    'en-IN': 'English', 'hi-IN': 'हिन्दी', 'kn-IN': 'ಕನ್ನಡ', 'te-IN': 'తెలుగు', 'ta-IN': 'தமிழ்',
    'mr-IN': 'मराठी', 'bn-IN': 'বাংলা', 'gu-IN': 'ગુજરાતી', 'ml-IN': 'മലയാളം', 'pa-IN': 'ਪੰਜਾਬੀ',
    'od-IN': 'ଓଡ଼ିଆ',
}


class SarvamError(Exception):
    pass


def is_configured():
    return bool(settings.SARVAM_API_KEY)


def _post(path, **kwargs):
    if not is_configured():
        raise SarvamError('SARVAM_API_KEY is not configured.')
    try:
        resp = requests.post(f'{API_BASE}{path}', headers={'api-subscription-key': settings.SARVAM_API_KEY},
                             timeout=30, **kwargs)
    except requests.RequestException as exc:
        raise SarvamError(f'Sarvam AI unreachable: {exc}') from exc
    if resp.status_code != 200:
        raise SarvamError(f'Sarvam AI error {resp.status_code}: {resp.text[:200]}')
    return resp.json()


def detect_language(text):
    """Return a BCP-47 code such as 'kn-IN' (English for unsupported or Latin-script English)."""
    data = _post('/text-lid', json={'input': text[:1000]})
    code = data.get('language_code')
    return code if code in LANGUAGES else ENGLISH


def _chunks(text, limit):
    """Split on line breaks so each request stays under the model's character limit."""
    chunk = ''
    for line in text.splitlines(keepends=True):
        if chunk and len(chunk) + len(line) > limit:
            yield chunk
            chunk = ''
        chunk += line
    if chunk:
        yield chunk


def translate(text, source, target, kind='answer'):
    """Translate text; kind='query' for a farmer's question, 'answer' for knowledge-base replies."""
    if source == target or not text.strip():
        return text
    model, limit = (QUERY_MODEL, QUERY_MAX_CHARS) if kind == 'query' else (ANSWER_MODEL, ANSWER_MAX_CHARS)
    key = 'sarvam:tr:' + hashlib.sha256(f'{model}|{source}|{target}|{text}'.encode()).hexdigest()
    if (cached := cache.get(key)) is not None:
        return cached
    parts = []
    for chunk in _chunks(text, limit):
        data = _post('/translate', json={
            'input': chunk, 'source_language_code': source, 'target_language_code': target,
            'model': model, 'mode': 'formal',
        })
        parts.append(data.get('translated_text', ''))
    result = ''.join(parts)
    cache.set(key, result, TRANSLATION_CACHE_SECONDS)
    return result


def transcribe(audio_file):
    """Speech-to-text with automatic language detection. Returns (transcript, language_code)."""
    files = {'file': (audio_file.name or 'audio.webm', audio_file.read(), audio_file.content_type or 'audio/webm')}
    data = _post('/speech-to-text', files=files, data={'model': STT_MODEL, 'language_code': 'unknown'})
    code = data.get('language_code')
    return data.get('transcript', '').strip(), (code if code in LANGUAGES else ENGLISH)
