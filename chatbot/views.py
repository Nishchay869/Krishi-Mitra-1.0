from django.utils.translation import gettext as _
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import multilingual, sarvam
from accounts.languages import SARVAM_CODES
from .models import ChatMessage

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 1000
MAX_AUDIO_BYTES = 5 * 1024 * 1024  # ~2-3 minutes of compressed speech


@login_required
def chat_page(request):
    # Whenever the user navigates to the Farm Assistant section, prior messages are cleared
    if request.user.is_authenticated:
        ChatMessage.objects.filter(user=request.user).delete()
    elif request.session.session_key:
        ChatMessage.objects.filter(session_key=request.session.session_key).delete()
    user_name = (request.user.first_name or request.user.username or '').strip().title()
    return render(request, 'chatbot/chat.html', {
        'history': [],
        'history_json': '[]',
        'user_name': user_name or 'Farmer',
    })


@require_POST
def api_chat(request):
    try:
        data = json.loads(request.body or '{}')
        message = data.get('message', '')
        language = data.get('language')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)
    message = str(message).strip()[:MAX_MESSAGE_LENGTH]
    if not message:
        return JsonResponse({'error': _('Message is required.')}, status=400)

    return JsonResponse(_answer(request, message, language=language))


@csrf_exempt
@require_POST
def api_clear(request):
    """Clear all chat history for the current user or session from the database."""
    deleted_count = 0
    if request.user.is_authenticated:
        deleted_count, _ = ChatMessage.objects.filter(user=request.user).delete()
    elif request.session.session_key:
        deleted_count, _ = ChatMessage.objects.filter(session_key=request.session.session_key).delete()
    return JsonResponse({'status': 'cleared', 'count': deleted_count})


def _transcribe(request):
    """Return (transcript, language, None) or (None, None, error JsonResponse)."""
    audio = request.FILES.get('audio')
    if not audio:
        return None, None, JsonResponse({'error': _('Audio file is required.')}, status=400)
    if audio.size > MAX_AUDIO_BYTES:
        return None, None, JsonResponse({'error': _('Recording is too long. Please keep it under 30 seconds.')}, status=400)
    try:
        transcript, language = sarvam.transcribe(audio)
    except sarvam.SarvamError:
        return None, None, JsonResponse({'error': _('Voice service is unavailable right now. Please type your question.')}, status=503)
    if not transcript:
        return None, None, JsonResponse({'error': _("Sorry, I couldn't hear that clearly. Please try again.")}, status=422)
    return transcript[:MAX_MESSAGE_LENGTH], language, None


@require_POST
def api_voice(request):
    """Live conversation turn: speech in, answer out."""
    transcript, language, error = _transcribe(request)
    if error:
        return error
    return JsonResponse({'transcript': transcript, **_answer(request, transcript, language, True)})


@require_POST
def api_transcribe(request):
    """Dictation: speech to text only. The farmer reviews the text and sends it like a typed question."""
    transcript, language, error = _transcribe(request)
    return error or JsonResponse({'transcript': transcript, 'language': language})


GREETING_IDENTITY = (
    "I'm Krishi Mitra, your farming assistant. You can ask me about crops, fertilizers, pests and diseases, "
    'weather, market prices or government schemes, in your own language. How can I help you today?'
)


def greeting_text(name, hour):
    """English greeting for the start of a live conversation; hour is the farmer's local hour (0-23)."""
    if 5 <= hour < 12:
        salutation = 'Good morning'
    elif 12 <= hour < 17:
        salutation = 'Good afternoon'
    elif 17 <= hour < 22:
        salutation = 'Good evening'
    else:
        salutation = 'Hello'
    return f'{salutation}, {name}! {GREETING_IDENTITY}' if name else f'{salutation}! {GREETING_IDENTITY}'


@require_POST
def api_greeting(request):
    """Spoken welcome when a live voice conversation opens, in the farmer's preferred language."""
    try:
        hour = int(json.loads(request.body or '{}').get('hour'))
        if not 0 <= hour <= 23:
            raise ValueError
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': _('hour (0-23) is required.')}, status=400)

    name, language = '', sarvam.ENGLISH
    if request.user.is_authenticated:
        name = (request.user.first_name or request.user.email or request.user.username).strip().title()
        code = SARVAM_CODES.get(request.user.profile.preferred_language, sarvam.ENGLISH)
        language = code if code in sarvam.LANGUAGES else sarvam.ENGLISH

    text = greeting_text(name, hour)
    audios = []
    try:
        text = sarvam.translate(text, sarvam.ENGLISH, language)
        audios = sarvam.speak(text, language)
    except sarvam.SarvamError:
        language = sarvam.ENGLISH  # still greet on screen; the conversation starts without audio
        text = greeting_text(name, hour)
    return JsonResponse({'text': text, 'language': language, 'audios': audios})


@require_POST
def api_speak(request, pk):
    """Read a bot reply aloud. Only the asker's own stored replies can be spoken, so the
    endpoint cannot be used to synthesise arbitrary text on our Sarvam account."""
    msg = get_object_or_404(ChatMessage, pk=pk)
    owns = (msg.user_id == request.user.id) if request.user.is_authenticated else \
        (msg.user_id is None and msg.session_key and msg.session_key == request.session.session_key)
    if not owns:
        return JsonResponse({'error': _('Not found.')}, status=404)
    try:
        audios = sarvam.speak_reply(msg.response_en or msg.response, msg.language)
    except sarvam.SarvamError:
        return JsonResponse({'error': _('Voice reply is unavailable right now.')}, status=503)
    return JsonResponse({'audios': audios, 'format': 'mp3'})


def _preferred_language(request):
    """The farmer's saved reply language (Sarvam code), or None for English."""
    if request.user.is_authenticated:
        code = SARVAM_CODES.get(request.user.profile.preferred_language, sarvam.ENGLISH)
        if code in sarvam.LANGUAGES and code != sarvam.ENGLISH:
            return code
    return None


def _store(request, message, reply, text, language, message_en, preferred, is_voice=False):
    """Save the exchange to chat history and build the API response body."""
    msg = ChatMessage.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        message=message,
        message_en=message_en if message_en != message else '',
        language=language,
        is_voice=is_voice,
        response=text,
        response_en=reply.text,
        intent=reply.intent,
        matched_entry=None,
        confidence=reply.confidence,
    )
    return {**reply.as_dict(), 'reply': text, 'language': language, 'message_id': msg.pk,
            'translation_unavailable': bool(preferred and language != preferred)}


def _answer(request, message, language=None, is_voice=False):
    preferred = _preferred_language(request)
    reply, text, language, message_en = multilingual.respond(message, language, output_language=preferred)
    if not request.session.session_key:
        request.session.save()
    return _store(request, message, reply, text, language, message_en, preferred, is_voice)


@require_POST
def api_chat_stream(request):
    """Like api_chat, but sends the reply piece by piece while it is written.

    Response: one JSON object per line (application/x-ndjson):
      {"type": "delta", "text": "..."}         more reply text, append it
      {"type": "replace", "text": "..."}       final text differs (e.g. translated), show this instead
      {"type": "done", ...same fields as api_chat}
      {"type": "error", "error": "..."}
    """
    try:
        data = json.loads(request.body or '{}')
        message = str(data.get('message', '')).strip()[:MAX_MESSAGE_LENGTH]
        language = data.get('language')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)
    if not message:
        return JsonResponse({'error': _('Message is required.')}, status=400)

    preferred = _preferred_language(request)
    if not request.session.session_key:
        request.session.save()  # must happen before streaming starts: cookies cannot be set later

    def events():
        streamed = []
        try:
            for kind, value in multilingual.respond_stream(message, language, output_language=preferred):
                if kind == 'delta':
                    streamed.append(value)
                    yield json.dumps({'type': 'delta', 'text': value}, ensure_ascii=False) + '\n'
                else:
                    reply, text, reply_language, message_en = value
            body = _store(request, message, reply, text, reply_language, message_en, preferred)
        except Exception:
            logger.exception('Streaming chat reply failed')
            yield json.dumps({'type': 'error', 'error': _('Sorry, the reply was interrupted. Please try again.')}) + '\n'
            return
        if text != ''.join(streamed):
            yield json.dumps({'type': 'replace', 'text': text}, ensure_ascii=False) + '\n'
        yield json.dumps({'type': 'done', **body}, ensure_ascii=False) + '\n'

    response = StreamingHttpResponse(events(), content_type='application/x-ndjson; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # ask proxies not to hold the stream back
    return response
