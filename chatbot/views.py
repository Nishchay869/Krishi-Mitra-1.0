import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from . import engine
from .models import ChatMessage

MAX_MESSAGE_LENGTH = 1000


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

    reply = engine.answer(message)
    if not request.session.session_key:
        request.session.save()
    ChatMessage.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or '',
        message=message,
        response=reply.text,
        intent=reply.intent,
        matched_entry=reply.entry,
        confidence=reply.confidence,
    )
    return JsonResponse(reply.as_dict())
