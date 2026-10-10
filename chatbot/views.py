import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import multilingual, sarvam
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
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    message = str(message).strip()[:MAX_MESSAGE_LENGTH]
    if not message:
        return JsonResponse({'error': 'Message is required.'}, status=400)

    return JsonResponse(_answer(request, message))


@require_POST
def api_voice(request):
    audio = request.FILES.get('audio')
    if not audio:
        return JsonResponse({'error': 'Audio file is required.'}, status=400)
    if audio.size > MAX_AUDIO_BYTES:
        return JsonResponse({'error': 'Recording is too long. Please keep it under 2 minutes.'}, status=400)
    try:
        transcript, language = sarvam.transcribe(audio)
    except sarvam.SarvamError:
        return JsonResponse({'error': 'Voice service is unavailable right now. Please type your question.'}, status=503)
    if not transcript:
        return JsonResponse({'error': "Sorry, I couldn't hear that clearly. Please try again."}, status=422)
    return JsonResponse({'transcript': transcript, **_answer(request, transcript[:MAX_MESSAGE_LENGTH], language, True)})


def _answer(request, message, language=None, is_voice=False):
    reply, text, language, message_en = multilingual.respond(message, language)
    if not request.session.session_key:
        request.session.save()
    ChatMessage.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        message=message,
        message_en=message_en if message_en != message else '',
        language=language,
        is_voice=is_voice,
        response=text,
        intent=reply.intent,
        matched_entry=reply.entry,
        confidence=reply.confidence,
    )
    return {**reply.as_dict(), 'reply': text, 'language': language}
