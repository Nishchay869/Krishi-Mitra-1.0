"""Voice input (speech-to-text) and voice replies (text-to-speech): Gemini first, Sarvam as backup.

- transcribe(audio) -> (transcript, language): the recording (browser WebM/Ogg/WAV) is sent to
  Gemini, which writes it down in the language and script that was spoken.
- speak(text, language) -> (clips, format): Gemini speech, returned as base64 MP3 clips; long
  replies are split and generated in parallel. Cached for a day.
Both fall back to Sarvam if Gemini fails (Sarvam needs credits; it returns MP3 clips).
"""
import base64
import hashlib
import io
import json
import logging
import re
import wave
from concurrent.futures import ThreadPoolExecutor

import requests
from django.conf import settings
from django.core.cache import cache

from . import sarvam, translation

logger = logging.getLogger(__name__)

ENGLISH = sarvam.ENGLISH
LANGUAGES = sarvam.LANGUAGES
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
TTS_VOICE = 'Kore'                 # clear, calm voice
TTS_MAX_CHARS = 1200               # per clip; longer replies become several clips
TTS_PARALLEL = 3
TTS_CACHE_SECONDS = 24 * 60 * 60

TRANSCRIBE_PROMPT = (
    'This is a farmer\'s voice message for a farming assistant. Write down exactly what is said, '
    'in the language and script that is spoken (Kannada in Kannada script, Hindi in Devanagari, '
    'and so on). Do not translate or answer it. Reply as JSON: {"transcript": "...", "language": '
    '"<code>"} where <code> is one of: ' + ', '.join(sorted(LANGUAGES)) + '. If nothing is said, '
    'use an empty transcript.'
)


class VoiceError(sarvam.SarvamError):
    """Neither Gemini nor Sarvam could handle the audio (callers already handle SarvamError)."""


def _key():
    return getattr(settings, 'GEMINI_API_KEY', '')


def _post(model, body, timeout=60):
    try:
        resp = requests.post(ENDPOINT.format(model=model), params={'key': _key()}, json=body, timeout=(3, timeout))
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts']
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        # Never log the exception text: the request URL contains the API key.
        raise VoiceError(f'Gemini {model} request failed ({type(exc).__name__})') from None


# ── Voice input ──────────────────────────────────────────────────────────────

def _gemini_transcribe(audio_bytes, mime):
    model = getattr(settings, 'GEMINI_CHAT_MODEL', 'gemini-3.5-flash-lite')
    parts = _post(model, {
        'contents': [{'parts': [{'inline_data': {'mime_type': mime, 'data': base64.b64encode(audio_bytes).decode()}},
                                {'text': TRANSCRIBE_PROMPT}]}],
        'generationConfig': {'temperature': 0, 'responseMimeType': 'application/json'},
    }, timeout=45)
    try:
        data = json.loads(''.join(p.get('text', '') for p in parts if isinstance(p, dict)))
    except ValueError:
        raise VoiceError('Gemini transcription was not valid JSON') from None
    transcript = str(data.get('transcript') or '').strip()
    language = data.get('language')
    if language not in LANGUAGES:
        language = translation.detect_language(transcript) if transcript else ENGLISH
    return transcript, language


def transcribe(audio_file):
    """Speech-to-text with language detection. Returns (transcript, language_code)."""
    audio_bytes = audio_file.read()
    mime = (getattr(audio_file, 'content_type', '') or 'audio/webm').split(';')[0].strip() or 'audio/webm'
    if _key():
        try:
            return _gemini_transcribe(audio_bytes, mime)
        except VoiceError as exc:
            logger.warning('Gemini voice input failed: %s; trying Sarvam', exc)
    if sarvam.is_configured():
        audio_file.seek(0)
        return sarvam.transcribe(audio_file)
    raise VoiceError('No voice input service available')


# ── Voice replies ────────────────────────────────────────────────────────────

def _as_wav(audio_bytes, mime):
    """Gemini returns WAV, or raw 16-bit PCM ("audio/L16; rate=24000") on some models."""
    if audio_bytes[:4] == b'RIFF':
        return audio_bytes
    rate = int(re.search(r'rate=(\d+)', mime).group(1)) if 'rate=' in mime else 24000
    out = io.BytesIO()
    with wave.open(out, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(audio_bytes)
    return out.getvalue()


MP3_KBPS = 32                      # speech: ~12x smaller than WAV (70 s: 3.3 MB -> 0.28 MB)


def _compress(wav_bytes):
    """WAV -> MP3 so voice replies are light on mobile data. Returns (bytes, format);
    keeps WAV if the encoder is unavailable."""
    try:
        import lameenc
    except ImportError:
        return wav_bytes, 'wav'
    with wave.open(io.BytesIO(wav_bytes)) as w:
        rate, channels, frames = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(MP3_KBPS)
    encoder.set_in_sample_rate(rate)
    encoder.set_channels(channels)
    encoder.set_quality(5)
    return encoder.encode(frames) + encoder.flush(), 'mp3'


def _gemini_clip(text):
    model = getattr(settings, 'GEMINI_TTS_MODEL', 'gemini-3.8-flash-lite-tts')
    parts = _post(model, {
        'contents': [{'parts': [{'text': text}]}],
        'generationConfig': {'responseModalities': ['AUDIO'],
                             'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': TTS_VOICE}}}},
    })
    inline = next((p['inlineData'] for p in parts if isinstance(p, dict) and 'inlineData' in p), None)
    if not inline or not inline.get('data'):
        raise VoiceError('Gemini returned no audio')
    audio, fmt = _compress(_as_wav(base64.b64decode(inline['data']), inline.get('mimeType', '')))
    return base64.b64encode(audio).decode(), fmt


def speak(text, language):
    """Text-to-speech. Returns (list of base64 audio clips, format) - 'mp3' (or 'wav' without the encoder)."""
    if not text.strip():
        return [], 'wav'
    key = 'voice:tts:' + hashlib.sha256(f'{TTS_VOICE}|{language}|{text}'.encode()).hexdigest()
    if (cached := cache.get(key)) is not None:
        return cached
    if _key():
        try:
            chunks = list(sarvam._chunks(text, TTS_MAX_CHARS))
            with ThreadPoolExecutor(max_workers=min(TTS_PARALLEL, len(chunks))) as pool:
                clips = list(pool.map(_gemini_clip, chunks))
            result = ([clip for clip, _ in clips], clips[0][1])
            cache.set(key, result, TTS_CACHE_SECONDS)
            return result
        except VoiceError as exc:
            logger.warning('Gemini voice reply failed: %s; trying Sarvam', exc)
    if sarvam.is_configured():
        return sarvam.speak(text, language), 'mp3'
    raise VoiceError('No voice reply service available')


def speak_reply(text_en, language):
    """Speak a stored reply in the farmer's language, symbols removed (never re-translate Indic text)."""
    spoken = sarvam.speech_text(text_en)
    if language != ENGLISH and not sarvam.is_indic_script(spoken):
        spoken = translation.translate(spoken, ENGLISH, language)
    return speak(spoken, language)
