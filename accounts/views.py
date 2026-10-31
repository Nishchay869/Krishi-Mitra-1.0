import json
from django.contrib import messages
from django.templatetags.static import static
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import IntegrityError
from django.shortcuts import redirect, render

from chatbot.models import ChatMessage, KnowledgeEntry
from disease.views import get_user_diagnoses
from weather.spray import evaluate_spray_condition
from weather.services import fetch_forecast, fetch_village_forecast, WeatherError

from .forms import ProfileForm, RegisterForm
from .locations import state_districts
from .models import Feedback, PredictionLog
from .languages import available_languages
from .localization import ui_text
from .onboarding import CROP_GROUPS, GROWING_PLACES, FarmPreferencesForm
from django.views.decorators.http import require_POST

CROP_PHOTO_MAP = {name: photo for group, crops in CROP_GROUPS for name, photo in crops}
DEFAULT_CROP_NAMES = ['Tomato', 'Pepper bell', 'Rice', 'Cotton', 'Wheat']


def _crop_to_dict(crop_name):
    clean_name = str(crop_name).strip()
    photo = CROP_PHOTO_MAP.get(clean_name)
    if not photo:
        c_lower = clean_name.lower()
        for name, p in CROP_PHOTO_MAP.items():
            if name.lower() == c_lower:
                photo = p
                clean_name = name
                break
    slug = clean_name.lower().replace(' ', '-').replace('&', '').replace('(', '').replace(')', '')
    if not photo:
        photo = f'images/crops/{slug}.webp'

    display_name = _('Capsicum & Chilli') if clean_name == 'Pepper bell' else ui_text(clean_name)

    return {
        'id': slug,
        'name': clean_name,
        'display_name': display_name,
        'image': static(photo),
        'has_ring': False,
    }


def _get_home_weather(request):
    import datetime
    now = datetime.datetime.now()
    current_hour = now.hour
    is_daylight_now = (6 <= current_hour < 18)

    location = None
    village_lookup = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        p = request.user.profile
        village = p.village.strip()
        if village:
            village_lookup = (village, p.district.strip(), p.state.strip())
            location = ', '.join(part for part in village_lookup if part)
        elif p.district.strip() or p.state.strip():
            location = ', '.join(part for part in (p.district.strip(), p.state.strip()) if part)

    forecast_slot = None
    if location:
        try:
            days = (fetch_village_forecast(*village_lookup) if village_lookup else fetch_forecast(location))
            if days and days[0].get('slots'):
                forecast_slot = days[0]['slots'][0]
        except Exception:
            forecast_slot = None

    if not forecast_slot:
        for fallback_loc in ('Bengaluru', 'Delhi', 'Pune'):
            try:
                days = fetch_forecast(fallback_loc)
                if days and days[0].get('slots'):
                    forecast_slot = days[0]['slots'][0]
                    location = fallback_loc
                    break
            except Exception:
                continue

    if forecast_slot:
        temp = float(forecast_slot.get('temp', 24.0))
        humidity = float(forecast_slot.get('humidity', 60.0))
        wind_kmh = round(float(forecast_slot.get('wind', 2.5)) * 3.6, 1)
        rain_3h = (float(forecast_slot.get('rain', 0)) > 0) or (float(forecast_slot.get('pop', 0)) >= 0.3)
        rain_mm = float(forecast_slot.get('rain', 0))
        description = forecast_slot.get('description', 'Clear sky').capitalize()
        is_daylight = forecast_slot.get('daylight', is_daylight_now)
    else:
        temp = 22.0 if not is_daylight_now else 26.0
        humidity = 70.0 if not is_daylight_now else 55.0
        wind_kmh = 2.0 if not is_daylight_now else 8.5
        rain_3h = False
        rain_mm = 0.0
        description = 'Clear night' if not is_daylight_now else 'Clear sky'
        is_daylight = is_daylight_now

    eval_result = evaluate_spray_condition(
        temp, humidity, wind_kmh, rain_3h, rain_mm=rain_mm, is_daylight=is_daylight, current_hour=current_hour
    )
    status = eval_result['status']
    delta_t = eval_result['delta_t']

    if status == 'OPTIMAL':
        status_label = _('Optimal')
        badge_class = 'is-optimal'
        badge_icon = 'check'
        time_text = f"ΔT {delta_t}°C · " + _('Ideal window')
    elif status == 'MARGINAL':
        status_label = _('Marginal')
        badge_class = 'is-marginal'
        badge_icon = 'alert'
        time_text = f"ΔT {delta_t}°C · " + _('Monitor drift')
    else:
        status_label = _('Avoid')
        badge_class = 'is-avoid'
        badge_icon = 'x'
        if not is_daylight or current_hour < 6 or current_hour >= 18:
            time_text = _('Night time · Opens 06:00 AM')
        elif eval_result.get('rain_status') == 'poor':
            time_text = _('Rain imminent')
        elif eval_result.get('wind_status') == 'poor':
            time_text = _('High wind drift')
        elif temp > 35:
            time_text = _('High temperature')
        else:
            time_text = f"ΔT {delta_t}°C · " + _('Do not spray')

    return {
        'temp': round(temp),
        'temp_str': f"{round(temp)} °C",
        'humidity': round(humidity),
        'wind_kmh': round(wind_kmh, 1),
        'delta_t': delta_t,
        'rain_mm': round(rain_mm, 2),
        'rain_within_3h': rain_3h,
        'is_daylight': is_daylight,
        'status': status,
        'status_label': str(status_label),
        'badge_class': badge_class,
        'badge_icon': badge_icon,
        'time_text': str(time_text),
        'reason': eval_result['reason'],
        'description': description,
        'location': location or 'Local',
        'delta_t_range': eval_result.get('delta_t_range', '2-8'),
        'delta_t_status': eval_result.get('delta_t_status', 'optimal'),
        'rain_range': eval_result.get('rain_range', 'no_rain'),
        'rain_status': eval_result.get('rain_status', 'optimal'),
        'wind_range': eval_result.get('wind_range', '<12'),
        'wind_status': eval_result.get('wind_status', 'optimal'),
    }


def home(request):
    raw_crops = []
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        raw_crops = request.user.profile.selected_crops or []
    if not raw_crops:
        raw_crops = request.session.get('farm_preferences', {}).get('selected_crops', [])

    seen = set()
    unique_crops = []
    for c in raw_crops:
        if c and c not in seen:
            seen.add(c)
            unique_crops.append(c)

    if unique_crops:
        crops_list = [_crop_to_dict(c) for c in unique_crops]
        is_user_crops = True
    else:
        crops_list = [_crop_to_dict(c) for c in DEFAULT_CROP_NAMES]
        is_user_crops = False

    if crops_list:
        crops_list[0]['has_ring'] = True

    weather_data = _get_home_weather(request)
    recent_diagnoses = get_user_diagnoses(request, limit=6)

    context = {
        'user_crops': crops_list,
        'user_crops_json': json.dumps(crops_list),
        'has_user_crops': is_user_crops,
        'weather_data': weather_data,
        'weather_json': json.dumps(weather_data),
        'recent_diagnoses': recent_diagnoses,
        'diagnoses_json': json.dumps(recent_diagnoses),
    }
    return render(request, 'home.html', context)


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
    feedback_ratings_list = Feedback.objects.values_list('rating').annotate(n=Count('id'))
    feedback_ratings = {Feedback.RATING_GOOD: 0, Feedback.RATING_AVERAGE: 0, Feedback.RATING_BAD: 0}
    for r, count in feedback_ratings_list:
        feedback_ratings[r] = count

    return render(request, 'accounts/admin_dashboard.html', {
        'farmer_count': User.objects.filter(profile__role='farmer').count(),
        'chat_count': ChatMessage.objects.count(),
        'kb_count': KnowledgeEntry.objects.filter(is_active=True).count(),
        'prediction_counts': dict(PredictionLog.objects.values_list('kind').annotate(n=Count('id'))),
        'unanswered': ChatMessage.objects.filter(matched_entry__isnull=True).exclude(
            intent__in=['greeting', 'weather'])[:10],
        'top_intents': ChatMessage.objects.values('intent').annotate(n=Count('id')).order_by('-n')[:6],
        'recent_predictions': PredictionLog.objects.select_related('user')[:10],
        'feedback_count': Feedback.objects.count(),
        'feedback_ratings': feedback_ratings,
        'recent_feedbacks': Feedback.objects.select_related('user')[:15],
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


def settings_view(request):
    """View and manage application preferences."""
    lang_choices = available_languages()
    current_lang = getattr(request, 'LANGUAGE_CODE', 'en')
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        current_lang = request.user.profile.preferred_language or current_lang

    if request.method == 'POST':
        new_lang = request.POST.get('preferred_language')
        if new_lang and new_lang in dict(lang_choices):
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                request.user.profile.preferred_language = new_lang
                request.user.profile.save(update_fields=['preferred_language'])
            translation.activate(new_lang)
            request.LANGUAGE_CODE = new_lang

        messages.success(request, _('Settings updated successfully.'))
        response = redirect('accounts:settings')
        if new_lang:
            response.set_cookie('django_language', new_lang, max_age=365 * 24 * 60 * 60, samesite='Lax')
        return response

    return render(request, 'accounts/settings.html', {
        'available_languages': lang_choices,
        'current_language': current_lang,
    })


@require_POST
def settings_api(request):
    """API endpoint to update user settings asynchronously."""
    from django.http import JsonResponse
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            pass
    else:
        data = request.POST

    new_lang = data.get('preferred_language')
    lang_choices = dict(available_languages())
    response_data = {'success': True}

    if new_lang and new_lang in lang_choices:
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            request.user.profile.preferred_language = new_lang
            request.user.profile.save(update_fields=['preferred_language'])
        translation.activate(new_lang)
        request.LANGUAGE_CODE = new_lang
        response_data['language'] = new_lang

    res = JsonResponse(response_data)
    if new_lang:
        res.set_cookie('django_language', new_lang, max_age=365 * 24 * 60 * 60, samesite='Lax')
    return res


@require_POST
def submit_feedback(request):
    """API endpoint to receive user experience feedback for Krishi Mitra app."""
    from django.http import JsonResponse
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            pass
    else:
        data = request.POST

    rating = str(data.get('rating', '')).strip().lower()
    comment = str(data.get('comment', '')).strip()

    valid_ratings = [Feedback.RATING_BAD, Feedback.RATING_AVERAGE, Feedback.RATING_GOOD]
    if rating not in valid_ratings:
        return JsonResponse({
            'success': False,
            'error': f"Rating must be one of {', '.join(valid_ratings)}"
        }, status=400)

    user = request.user if request.user.is_authenticated else None
    feedback = Feedback.objects.create(
        user=user,
        rating=rating,
        comment=comment,
    )
    return JsonResponse({
        'success': True,
        'id': feedback.id,
        'rating': feedback.rating,
        'message': _('Thank you for your feedback!')
    })


