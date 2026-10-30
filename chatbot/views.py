from django.utils.translation import gettext as _
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from . import multilingual, sarvam
from accounts.languages import SARVAM_CODES
from .models import ChatMessage

MAX_MESSAGE_LENGTH = 1000
MAX_AUDIO_BYTES = 5 * 1024 * 1024  # ~2-3 minutes of compressed speech


@login_required
def chat_page(request):
    history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'chatbot/chat.html', {'history': reversed(list(history))})


@require_POST
def api_chat(request):
    try:
        message = json.loads(request.body or '{}').get('message', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)
    message = str(message).strip()[:MAX_MESSAGE_LENGTH]
    if not message:
        return JsonResponse({'error': _('Message is required.')}, status=400)

    return JsonResponse(_answer(request, message))


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


def _answer(request, message, language=None, is_voice=False):
    preferred = None
    if request.user.is_authenticated:
        code = SARVAM_CODES.get(request.user.profile.preferred_language, sarvam.ENGLISH)
        if code in sarvam.LANGUAGES and code != sarvam.ENGLISH:
            preferred = code
    reply, text, language, message_en = multilingual.respond(message, language, output_language=preferred)
    if not request.session.session_key:
        request.session.save()
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
        matched_entry=reply.entry,
        confidence=reply.confidence,
    )
    return {**reply.as_dict(), 'reply': text, 'language': language, 'message_id': msg.pk,
            'translation_unavailable': bool(preferred and language != preferred)}
