from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .planner import build_plan
from accounts.onboarding import CROP_CHOICES

from .services import WeatherError, advisories, fetch_forecast, fetch_village_forecast


def _parse_moisture(raw):
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if 0 <= value <= 100 else None


@login_required
def weather_page(request):
    profile = request.user.profile
    village = profile.village.strip()
    saved_location = ', '.join(part.strip() for part in (village,profile.district,profile.state) if part.strip()) if village else ''
    entered_location = request.GET.get('location','').strip()
    use_saved_village = bool(village) and entered_location in ('',village,saved_location)
    location = saved_location if use_saved_village else entered_location
    village_lookup = (village,profile.district,profile.state) if use_saved_village else None
    if entered_location and not use_saved_village:
        parts = [part.strip() for part in entered_location.split(',')]
        if parts[-1].casefold() in ('india','in'):
            parts.pop()
        if len(parts) == 3 and all(parts):
            village_lookup = tuple(parts)
    soil_moisture = _parse_moisture(request.GET.get('soil_moisture'))
    soil = request.GET.get('soil','unknown')
    soil = soil if soil in ('dry','moist','wet') else 'unknown'
    saved_crops = [c for c in request.user.profile.selected_crops if c in dict(CROP_CHOICES)]
    days, notes, error = [], [], None
    if location:
        try:
            days = (fetch_village_forecast(*village_lookup)
                    if village_lookup else fetch_forecast(location))
            # Do not prescribe irrigation from universal raw VWC thresholds.
            notes = []
        except WeatherError as exc:
            error = _('Weather is unavailable. Check the location or try again later.')
    return render(request, 'weather/weather.html', {
        'plan':build_plan(days,saved_crops,request.user.profile.growing_place,soil),
        'saved_crops':saved_crops,'soil':soil, 'needs_village':not bool(village),
        'village_forecast':bool(village_lookup),
        'location': location, 'soil_moisture': soil_moisture, 'days': days, 'notes': notes, 'error': error,
    })


def api_weather(request):
    location = request.GET.get('location', '').strip()
    if not location:
        return JsonResponse({'error': _('location query parameter is required.')}, status=400)
    try:
        days = fetch_forecast(location)
    except WeatherError as exc:
        return JsonResponse({'error': _('Weather is unavailable. Check the location or try again later.')}, status=502)
    notes = advisories(days, _parse_moisture(request.GET.get('soil_moisture')))
    return JsonResponse({'location': location, 'forecast': days,
                         'advisories': [{'level': lvl, 'text': txt} for lvl, txt in notes]})
