"""OpenWeatherMap integration and rule-based farm advisories (spec §3.5)."""
from collections import defaultdict
from datetime import datetime

import requests
from django.conf import settings
from django.core.cache import cache

FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'
CACHE_SECONDS = 30 * 60


class WeatherError(Exception):
    pass


def fetch_forecast(location):
    """Return a list of daily summaries for `location` (up to 5 days)."""
    if not settings.OPENWEATHER_API_KEY:
        raise WeatherError('OPENWEATHER_API_KEY is not configured on the server.')
    cache_key = f'owm:{location.lower().strip()}'
    if (cached := cache.get(cache_key)) is not None:
        return cached

    try:
        resp = requests.get(
            FORECAST_URL,
            params={'q': location, 'appid': settings.OPENWEATHER_API_KEY, 'units': 'metric'},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise WeatherError(f'Weather service unreachable: {exc}') from exc
    if resp.status_code == 404:
        raise WeatherError(f'Location "{location}" not found. Try your district or nearest town name.')
    if resp.status_code != 200:
        raise WeatherError(f'Weather service error ({resp.status_code}).')

    days = summarize(resp.json())
    cache.set(cache_key, days, CACHE_SECONDS)
    return days


def summarize(payload):
    """Collapse OpenWeatherMap 3-hourly entries into per-day summaries."""
    buckets = defaultdict(list)
    for item in payload.get('list', []):
        buckets[datetime.fromtimestamp(item['dt']).date()].append(item)

    days = []
    for day, items in sorted(buckets.items()):
        days.append({
            'date': day.isoformat(),
            'temp_min': round(min(i['main']['temp_min'] for i in items), 1),
            'temp_max': round(max(i['main']['temp_max'] for i in items), 1),
            'humidity': round(sum(i['main']['humidity'] for i in items) / len(items)),
            'pressure': round(sum(i['main']['pressure'] for i in items) / len(items)),
            'wind_speed': round(max(i['wind']['speed'] for i in items), 1),
            'rain_mm': round(sum(i.get('rain', {}).get('3h', 0) for i in items), 1),
            'description': max(
                (i['weather'][0]['description'] for i in items),
                key=lambda d: sum(1 for i in items if i['weather'][0]['description'] == d),
            ),
        })
    return days[:5]


def advisories(days, soil_moisture=None):
    """Rule-based advisories from the forecast and an optional soil-moisture reading (% VWC)."""
    if not days:
        return []
    notes = []
    next3 = days[:3]
    rain_next3 = sum(d['rain_mm'] for d in next3)

    if soil_moisture is not None:
        if soil_moisture < 25 and rain_next3 < 5:
            notes.append(('warning', f'Soil moisture is low ({soil_moisture}%) and little rain is expected. Irrigate in the next 24 hours, preferably early morning or evening.'))
        elif soil_moisture < 25:
            notes.append(('info', f'Soil moisture is low ({soil_moisture}%) but about {rain_next3:.0f} mm rain is forecast in 3 days. Consider a light irrigation only if crops are wilting.'))
        elif soil_moisture > 60:
            notes.append(('info', f'Soil moisture is high ({soil_moisture}%). Skip irrigation and ensure field drainage.'))
        else:
            notes.append(('success', f'Soil moisture ({soil_moisture}%) is adequate. No irrigation needed today.'))

    if rain_next3 >= 20:
        notes.append(('warning', f'Heavy rain (~{rain_next3:.0f} mm) expected in the next 3 days. Postpone irrigation, fertilizer top-dressing and pesticide sprays; clear field drainage channels.'))
    elif rain_next3 >= 5:
        notes.append(('info', f'Moderate rain (~{rain_next3:.0f} mm) expected. Plan sprays for dry windows so they are not washed off.'))
    elif soil_moisture is None:
        notes.append(('info', 'Little rain expected in the next 3 days. Check soil moisture and irrigate if the top 5 cm of soil is dry.'))

    if max(d['temp_max'] for d in next3) >= 38:
        notes.append(('warning', 'High temperatures (38 °C+) expected. Irrigate in the evening, mulch to conserve moisture, and protect nursery seedlings and livestock from heat.'))
    if min(d['temp_min'] for d in next3) <= 4:
        notes.append(('warning', 'Frost risk: near-freezing nights expected. Give a light irrigation in the evening and cover sensitive seedlings.'))
    if sum(d['humidity'] for d in next3) / len(next3) >= 85:
        notes.append(('warning', 'Sustained high humidity favours fungal diseases (blight, mildew, blast). Scout fields closely and consider a preventive fungicide spray.'))
    if max(d['wind_speed'] for d in next3) >= 8:
        notes.append(('info', 'Strong winds expected. Avoid spraying pesticides (drift risk) and stake tall crops.'))
    return notes
