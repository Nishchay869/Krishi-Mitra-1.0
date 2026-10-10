from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import WeatherError, advisories, fetch_forecast


def _parse_moisture(raw):
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if 0 <= value <= 100 else None


@login_required
def weather_page(request):
    location = request.GET.get('location', '').strip() or request.user.profile.location_query
    soil_moisture = _parse_moisture(request.GET.get('soil_moisture'))
    days, notes, error = [], [], None
    if location:
        try:
            days = fetch_forecast(location)
            notes = advisories(days, soil_moisture)
        except WeatherError as exc:
            error = str(exc)
    return render(request, 'weather/weather.html', {
        'location': location, 'soil_moisture': soil_moisture, 'days': days, 'notes': notes, 'error': error,
    })


def api_weather(request):
    location = request.GET.get('location', '').strip()
    if not location:
        return JsonResponse({'error': 'location query parameter is required.'}, status=400)
    try:
        days = fetch_forecast(location)
    except WeatherError as exc:
        return JsonResponse({'error': str(exc)}, status=502)
    notes = advisories(days, _parse_moisture(request.GET.get('soil_moisture')))
    return JsonResponse({'location': location, 'forecast': days,
                         'advisories': [{'level': lvl, 'text': txt} for lvl, txt in notes]})
