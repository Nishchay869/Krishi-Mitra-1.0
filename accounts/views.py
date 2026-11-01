import datetime
import json
from django.contrib import messages
from django.templatetags.static import static
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from chatbot.models import ChatMessage, KnowledgeEntry
from crops.models import CropStatus
from disease.views import get_user_diagnoses
from weather.spray import evaluate_spray_condition, build_hourly_spray_forecast
from weather.services import fetch_forecast, fetch_village_forecast, WeatherError

from .forms import EmailLoginForm, ProfileForm, RegisterForm
from .locations import state_districts
from .models import Feedback, PredictionLog
from .languages import available_languages
from .localization import ui_text
from .onboarding import CROP_GROUPS, GROWING_PLACES, FarmPreferencesForm
from django.views.decorators.http import require_POST

CROP_PHOTO_MAP = {name: photo for group, crops in CROP_GROUPS for name, photo in crops}
DEFAULT_CROP_NAMES = ['Tomato', 'Pepper bell', 'Rice', 'Cotton', 'Wheat']


def _format_time_ago(dt):
    diff = timezone.now() - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return 'Just now'
    minutes = seconds // 60
    if minutes < 60:
        return f'{minutes}m ago'
    hours = minutes // 60
    if hours < 24:
        return f'{hours}h ago'
    days = hours // 24
    return f'{days}d ago'


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
        'has_story': False,
        'stories': [],
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

    days = None
    if location:
        try:
            days = (fetch_village_forecast(*village_lookup) if village_lookup else fetch_forecast(location))
        except Exception:
            days = None

    if not days:
        for fallback_loc in ('Bengaluru', 'Delhi', 'Pune'):
            try:
                days = fetch_forecast(fallback_loc)
                if days and days[0].get('slots'):
                    location = fallback_loc
                    break
            except Exception:
                continue

    current_temp = 22 if not is_daylight_now else 26
    temp_min = 18
    temp_max = 29
    rain_val = 0.0
    description = 'Clear night' if not is_daylight_now else 'Clear sky'

    if days and days[0].get('slots'):
        first_day = days[0]
        first_slot = first_day['slots'][0]
        current_temp = round(first_slot.get('temp', 22))
        temp_min = round(first_day.get('temp_min', current_temp - 4))
        temp_max = round(first_day.get('temp_max', current_temp + 7))
        rain_raw = first_slot.get('rain', 0.0)
        rain_val = float(rain_raw.get('3h', 0.0) if isinstance(rain_raw, dict) else (rain_raw or 0.0))
        description = first_slot.get('description', 'Clear sky').capitalize()

    spray_res = build_hourly_spray_forecast(
        temp_min=temp_min,
        temp_max=temp_max,
        current_temp=current_temp,
        now_hour=current_hour,
        rain_mm=rain_val,
    )
    weather_data = spray_res['weather_data']
    weather_data['description'] = description
    weather_data['location'] = location or 'Local'
    return weather_data


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

    # Fetch active, unexpired crop statuses / stories uploaded by admin
    now = timezone.now()
    active_statuses = CropStatus.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).select_related('author').order_by('-created_at')

    statuses_by_slug = {}
    universal_statuses = []
    for st in active_statuses:
        st_data = {
            'id': st.id,
            'title': st.title,
            'caption': st.caption,
            'badge': st.get_badge_display(),
            'badge_key': st.badge,
            'image': st.image_url,
            'crop_name': st.crop_name,
            'author': st.author.first_name or st.author.username if st.author else 'Krishi Mitra Agronomist',
            'created_at': st.created_at.strftime('%d %b, %I:%M %p'),
            'time_ago': _format_time_ago(st.created_at),
        }
        if st.crop_slug in ('all', 'all-crops'):
            universal_statuses.append(st_data)
        else:
            statuses_by_slug.setdefault(st.crop_slug.lower(), []).append(st_data)

    # Attach active stories to matching crops
    for crop in crops_list:
        c_slug = crop['id'].lower()
        c_stories = statuses_by_slug.get(c_slug, []) + universal_statuses
        if c_stories:
            crop['has_story'] = True
            crop['has_ring'] = True
            crop['stories'] = c_stories
        else:
            crop['has_story'] = False
            crop['stories'] = []

    if crops_list and not any(c.get('has_story') for c in crops_list):
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


def login_view(request):
    portal = request.GET.get('portal', '').strip().lower()
    if request.method == 'POST':
        portal = request.POST.get('portal', portal or 'farmer').strip().lower()
    if not portal or portal not in ('farmer', 'admin'):
        portal = 'farmer'

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.user.is_authenticated:
        if portal == 'admin' and getattr(getattr(request.user, 'profile', None), 'is_admin', False):
            return redirect('accounts:admin_dashboard')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('accounts:dashboard')

    form = EmailLoginForm(request=request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if hasattr(user, 'profile') and user.profile.preferred_language:
            translation.activate(user.profile.preferred_language)
            request.LANGUAGE_CODE = user.profile.preferred_language

        if portal == 'admin' or (getattr(getattr(user, 'profile', None), 'is_admin', False) and not next_url):
            return redirect('accounts:admin_dashboard')

        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('accounts:dashboard')

    return render(request, 'accounts/login.html', {
        'form': form,
        'portal': portal,
        'next': next_url,
    })


def admin_login_redirect(request):
    return redirect('/accounts/login/?portal=admin')


@user_passes_test(_is_admin, login_url='accounts:login')
def admin_dashboard(request):
    feedback_ratings_list = Feedback.objects.values_list('rating').annotate(n=Count('id'))
    feedback_ratings = {Feedback.RATING_GOOD: 0, Feedback.RATING_AVERAGE: 0, Feedback.RATING_BAD: 0}
    for r, count in feedback_ratings_list:
        feedback_ratings[r] = count

    available_crops = [
        {'name': 'Tomato', 'slug': 'tomato'},
        {'name': 'Pepper bell', 'slug': 'pepper-bell', 'label': 'Capsicum & Chilli'},
        {'name': 'Rice', 'slug': 'rice'},
        {'name': 'Cotton', 'slug': 'cotton'},
        {'name': 'Wheat', 'slug': 'wheat'},
        {'name': 'Onion', 'slug': 'onion'},
        {'name': 'Garlic', 'slug': 'garlic'},
        {'name': 'Potato', 'slug': 'potato'},
        {'name': 'Pomegranate', 'slug': 'pomegranate'},
        {'name': 'Corn (Maize)', 'slug': 'corn-maize'},
        {'name': 'All Crops (Universal Advisory)', 'slug': 'all'},
    ]

    active_statuses = CropStatus.objects.all().order_by('-created_at')[:30]

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
        'active_statuses': active_statuses,
        'available_crops': available_crops,
        'badge_choices': CropStatus.BADGE_CHOICES,
    })


@user_passes_test(_is_admin, login_url='accounts:login')
@require_POST
def admin_upload_status(request):
    """Admin endpoint to broadcast an Instagram-style status / story for a crop."""
    crop_name = request.POST.get('crop_name', '').strip()
    crop_slug = request.POST.get('crop_slug', '').strip().lower()
    title = request.POST.get('title', '').strip()
    caption = request.POST.get('caption', '').strip()
    badge = request.POST.get('badge', CropStatus.BADGE_ADVISORY)
    photo_file = request.FILES.get('photo')
    photo_url = request.POST.get('photo_url', '').strip()
    duration_hours = request.POST.get('duration_hours', '48')

    if not crop_name:
        crop_name = 'All Crops'
    if not crop_slug:
        crop_slug = crop_name.lower().replace(' ', '-').replace('&', '').replace('(', '').replace(')', '')

    expires_at = None
    try:
        hours = int(duration_hours)
        if hours > 0:
            expires_at = timezone.now() + datetime.timedelta(hours=hours)
    except (ValueError, TypeError):
        pass

    crop_status = CropStatus.objects.create(
        crop_name=crop_name,
        crop_slug=crop_slug,
        title=title or f'{crop_name} Advisory Update',
        caption=caption,
        badge=badge,
        photo=photo_file,
        photo_url=photo_url,
        author=request.user,
        is_active=True,
        expires_at=expires_at,
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'id': crop_status.id,
            'crop_name': crop_status.crop_name,
            'title': crop_status.title,
            'image_url': crop_status.image_url,
            'message': 'Crop status broadcasted successfully!',
        })

    messages.success(request, f'Crop status for {crop_name} broadcasted successfully!')
    return redirect('accounts:admin_dashboard')


@user_passes_test(_is_admin, login_url='accounts:login')
@require_POST
def admin_delete_status(request, status_id):
    """Admin endpoint to delete or deactivate a crop status."""
    status_obj = get_object_or_404(CropStatus, pk=status_id)
    crop_name = status_obj.crop_name
    status_obj.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return JsonResponse({
            'success': True,
            'message': f'Status for {crop_name} deleted.',
        })

    messages.success(request, f'Crop status for {crop_name} deleted.')
    return redirect('accounts:admin_dashboard')


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


