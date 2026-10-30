"""Sarvam AI client: language detection, translation and speech-to-text for Indian languages.

Docs: https://docs.sarvam.ai/api-reference-docs
"""
import hashlib
import re

import requests
from django.conf import settings
from django.core.cache import cache

API_BASE = 'https://api.sarvam.ai'
# mayura handles short, colloquial and romanised questions ("gehu me kitna khad") cleanly;
# sarvam-translate takes longer text, so it is used for knowledge-base answers.
QUERY_MODEL, QUERY_MAX_CHARS = 'mayura:v1', 1000
ANSWER_MODEL, ANSWER_MAX_CHARS = 'sarvam-translate:v1', 2000
STT_MODEL = 'saaras:v4'
# Female voice: priya (measured ~195 Hz pitch and the loudest of bulbul:v3's female voices).
# bulbul:v3 has no loudness setting, so the browser boosts volume (see static/js/chat.js).
TTS_MODEL, TTS_SPEAKER, TTS_MAX_CHARS = 'bulbul:v3', 'shreya', 2500
TTS_PACE = 1.25  # slightly slower than normal for clarity
TTS_CACHE_SECONDS = 24 * 60 * 60
TRANSLATION_CACHE_SECONDS = 7 * 24 * 60 * 60

ENGLISH = 'en-IN'
# Translation supports all 22 scheduled languages; detection/voice have narrower coverage.
from accounts.languages import LANGUAGE_CHOICES, SARVAM_CODES
LANGUAGES = {SARVAM_CODES[code]: label for code, label in LANGUAGE_CHOICES}
VOICE_LANGUAGES = {'en-IN', 'hi-IN', 'bn-IN', 'gu-IN', 'kn-IN', 'ml-IN',
                   'mr-IN', 'od-IN', 'pa-IN', 'ta-IN', 'te-IN'}



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
    model, limit = (QUERY_MODEL, QUERY_MAX_CHARS) if kind == 'query' and source in VOICE_LANGUAGES and target in VOICE_LANGUAGES else (ANSWER_MODEL, ANSWER_MAX_CHARS)
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


_WEB_ADDRESS = re.compile(r'\s*\(?\b[\w.-]+\.(?:gov|nic|org|res)\.in/?\)?')
_CODE_IN_BRACKETS = re.compile(r'\s*\((?:[A-Z][A-Z0-9-]*|\d+(?:\.\d+)? ?(?:WP|EC|SC|SG))\)')  # (MOP), (KVK), (75 WP)
_RATE = re.compile(r'(\d[\d,.]*\s*[A-Za-z]*)\s*/\s*([A-Za-z]+)')                           # 6,000/year, 5 g/litre


def speech_text(text):
    """Rewrite an English reply so text-to-speech reads only words, not symbols.

    Sarvam reads "/" as "by" and "+" as "plus", and spells out bracketed codes, so:
    "Rs 6,000/year" -> "6,000 rupees per year", "DAP + urea" -> "DAP and urea",
    "alkaline/sodic" -> "alkaline or sodic", "2-4 weeks" -> "2 to 4 weeks", and "(MOP)",
    "(75 WP)", web addresses are dropped.
    """
    text = _WEB_ADDRESS.sub('', text)
    text = _CODE_IN_BRACKETS.sub('', text)
    text = re.sub(r'\bRs\.? ?([\d,]+)', r'\1 rupees', text)
    text = _RATE.sub(r'\1 per \2', text)
    text = re.sub(r'\s*/\s*', ' or ', text)
    text = re.sub(r'\s*\+\s*', ' and ', text)
    text = re.sub(r'\b(\d{4})-(\d{3})-(\d{4})\b', r'\1 \2 \3', text)                 # phone 1800-180-1551
    text = re.sub(r'(\d(?:\s?[ap]m)?)\s*[–—-]\s*(\d)', r'\1 to \2', text)              # 2-4 weeks, 6 am - 10 pm
    text = re.sub(r'\s+[–—-]\s+', ', ', text)
    text = re.sub(r'\be\.g\.', 'for example', text)
    text = re.sub(r'^\s*[•*-]\s*', '', text, flags=re.MULTILINE)
    return re.sub(r'[ \t]+', ' ', text).strip()


def speak_reply(text_en, language):
    """Speak an English knowledge-base reply in the farmer's language, symbols removed."""
    spoken = speech_text(text_en)
    if language != ENGLISH:
        spoken = translate(spoken, ENGLISH, language)
    return speak(spoken, language)


def speak(text, language):
    """Female text-to-speech in the given language. Returns a list of base64 MP3 clips."""
    key = 'sarvam:tts:' + hashlib.sha256(f'{TTS_MODEL}|{TTS_SPEAKER}|{language}|{text}'.encode()).hexdigest()
    if (cached := cache.get(key)) is not None:
        return cached
    clips = []
    for chunk in _chunks(text, TTS_MAX_CHARS):
        data = _post('/text-to-speech', json={
            'text': chunk, 'language_code': language if language in LANGUAGES else ENGLISH,
            'model': TTS_MODEL, 'speaker': TTS_SPEAKER, 'pace': TTS_PACE, 'output_audio_codec': 'mp3',
        })
        clips.extend(data.get('audios', []))
    cache.set(key, clips, TTS_CACHE_SECONDS)
    return clips
