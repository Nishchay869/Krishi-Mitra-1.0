from django.contrib import messages
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import IntegrityError
from django.shortcuts import redirect, render

from chatbot.models import ChatMessage, KnowledgeEntry

from .forms import ProfileForm, RegisterForm
from .locations import state_districts
from .models import PredictionLog
from .languages import available_languages
from .onboarding import CROP_GROUPS, GROWING_PLACES, FarmPreferencesForm
from django.views.decorators.http import require_POST


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = RegisterForm(request.POST or None, initial={'preferred_language': request.session.get('signup_language', request.LANGUAGE_CODE)})
    if request.method == 'POST' and form.is_valid():
        try:
            user = form.save()
        except IntegrityError:
            # A concurrent signup may have claimed the email after form validation.
            if not User.objects.filter(email__iexact=form.cleaned_data['email']).exists():
                raise
            form.add_error('email', _('An account with this email already exists.'))
        else:
            return _finish_registration(request, user)
    stage = request.GET.get('stage', 'language')
    if request.method == 'POST' or stage not in {'language', 'tour', 'farm', 'growing', 'details'}:
        stage = 'details'
    preferences = request.session.get('farm_preferences', {})
    return render(request, 'accounts/register.html', {
        'form': form, 'stage': stage, 'languages': available_languages(),
        'state_districts': state_districts(),
        'selected_language': request.session.get('signup_language', request.LANGUAGE_CODE),
        'crop_groups': CROP_GROUPS, 'growing_places': GROWING_PLACES,
        'selected_crops': preferences.get('selected_crops', []),
        'growing_place': preferences.get('growing_place', ''),
    })


def _finish_registration(request, user):
    preferences = FarmPreferencesForm(request.session.get('farm_preferences', {}))
    if preferences.is_valid():
        user.profile.selected_crops = preferences.cleaned_data['selected_crops']
        user.profile.growing_place = preferences.cleaned_data['growing_place']
        user.profile.save(update_fields=['selected_crops', 'growing_place'])
    request.session.pop('farm_preferences', None)
    request.session.pop('signup_language', None)
    login(request, user)
    translation.activate(user.profile.preferred_language)
    request.LANGUAGE_CODE = user.profile.preferred_language
    messages.success(request, _('Welcome! Your farmer account is ready.'))
    return redirect('accounts:dashboard')



@require_POST
def onboarding(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    if request.POST.get('action') == 'language':
        language = request.POST.get('language')
        if language not in dict(available_languages()):
            return redirect('accounts:register')
        request.session['signup_language'] = language
        translation.activate(language)
        request.LANGUAGE_CODE = language
        response = redirect('/accounts/register/?stage=tour')
        response.set_cookie('django_language', language, max_age=365*24*60*60,
                            samesite='Lax', secure=request.is_secure())
        return response
    preferences = FarmPreferencesForm(request.POST)
    if preferences.is_valid():
        request.session['farm_preferences'] = preferences.cleaned_data
        if request.POST.get('action') == 'crops':
            return redirect('/accounts/register/?stage=growing')
        return redirect('/accounts/register/?stage=details')
    return redirect('/accounts/register/?stage=farm')


@login_required
def dashboard(request):
    if request.user.profile.is_admin:
        return redirect('accounts:admin_dashboard')
    return render(request, 'accounts/dashboard.html', {
        'growing_place_label': dict(GROWING_PLACES).get(request.user.profile.growing_place, ''),
        'predictions': PredictionLog.objects.filter(user=request.user)[:5],
        'chats': ChatMessage.objects.filter(user=request.user)[:5],
    })


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if request.method == 'POST' and form.is_valid():
        try:
            saved_profile = form.save()
        except IntegrityError:
            if not User.objects.filter(email__iexact=form.cleaned_data['email']).exclude(pk=request.user.pk).exists():
                raise
            form.add_error('email', _('An account with this email already exists.'))
        else:
            translation.activate(saved_profile.preferred_language)
            request.LANGUAGE_CODE = saved_profile.preferred_language
            messages.success(request, _('Profile updated.'))
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


def service_worker(request):
    from pathlib import Path
    import json
    from django.conf import settings
    from django.http import HttpResponse
    from chatbot.context_processors import _static_version
    manifest = json.loads((Path(settings.BASE_DIR) / 'static/i18n/manifest.json').read_text())
    prefix = 'const APP_VERSION = ' + json.dumps(manifest['version'] + '-' + _static_version()) + ';\n'
    script = (Path(settings.BASE_DIR) / 'static/js/service-worker.js').read_text()
    response = HttpResponse(prefix + script, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    response['Service-Worker-Allowed'] = '/'
    return response
