from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect, render

from chatbot.models import ChatMessage, KnowledgeEntry

from .forms import ProfileForm, RegisterForm
from .models import PredictionLog


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome! Your farmer account is ready.')
        return redirect('accounts:dashboard')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    if request.user.profile.is_admin:
        return redirect('accounts:admin_dashboard')
    return render(request, 'accounts/dashboard.html', {
        'predictions': PredictionLog.objects.filter(user=request.user)[:5],
        'chats': ChatMessage.objects.filter(user=request.user)[:5],
    })


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:dashboard')
    return render(request, 'accounts/profile.html', {'form': form})


def _is_admin(user):
    return user.is_authenticated and user.profile.is_admin


@user_passes_test(_is_admin, login_url='accounts:login')
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html', {
        'farmer_count': User.objects.filter(profile__role='farmer').count(),
        'chat_count': ChatMessage.objects.count(),
        'kb_count': KnowledgeEntry.objects.filter(is_active=True).count(),
        'prediction_counts': dict(PredictionLog.objects.values_list('kind').annotate(n=Count('id'))),
        'unanswered': ChatMessage.objects.filter(matched_entry__isnull=True).exclude(
            intent__in=['greeting', 'weather'])[:10],
        'top_intents': ChatMessage.objects.values('intent').annotate(n=Count('id')).order_by('-n')[:6],
        'recent_predictions': PredictionLog.objects.select_related('user')[:10],
    })
