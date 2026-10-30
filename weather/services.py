"""OpenWeatherMap integration and rule-based farm advisories (spec §3.5)."""
from collections import defaultdict
import hashlib
import math
import unicodedata
from datetime import datetime, timedelta, timezone

import requests
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.cache import cache

# Verified spelling used in BBMP's village/polling-place directory:
# https://site.bbmp.gov.in/PDF/Election/Urban1/AC_152_Byatarayanapura.pdf
VILLAGE_ALIASES = {('karnataka', 'hunasamaranalli'): 'Hunasamaranahalli'}

GEOCODING_URL = 'https://api.openweathermap.org/geo/1.0/direct'
FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'
CACHE_SECONDS = 30 * 60


class WeatherError(Exception):
    pass


def fetch_forecast(location, *, latitude=None, longitude=None):
    """Return a list of daily summaries for `location` (up to 5 days)."""
    if not settings.OPENWEATHER_API_KEY:
        raise WeatherError('OPENWEATHER_API_KEY is not configured on the server.')
    params = {'appid': settings.OPENWEATHER_API_KEY, 'units': 'metric'}
    if latitude is not None or longitude is not None:
        latitude, longitude = _coordinates(latitude, longitude)
        params.update(lat=latitude, lon=longitude)
        cache_key = f'owm:point:v1:{latitude:.6f}:{longitude:.6f}'
    else:
        params['q'] = location
        cache_key = f'owm:v2:{location.lower().strip()}'
    if (cached := cache.get(cache_key)) is not None:
        return cached

    try:
        resp = requests.get(
            FORECAST_URL,
            params=params,
            timeout=10,
        )
    except requests.RequestException as exc:
        raise WeatherError('Weather is unavailable. Check the location or try again later.') from None
    if resp.status_code == 404:
        raise WeatherError(f'Location "{location}" not found. Try your district or nearest town name.')
    if resp.status_code != 200:
        raise WeatherError(f'Weather service error ({resp.status_code}).')

    try:
        days = summarize(resp.json())
    except (ValueError, KeyError, TypeError, IndexError):
        raise WeatherError('Weather is unavailable. Check the location or try again later.') from None
    cache.set(cache_key, days, CACHE_SECONDS)
    return days


def _coordinates(latitude, longitude):
    try:
        lat, lon = float(latitude), float(longitude)
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError
        return lat, lon
    except (TypeError, ValueError, OverflowError):
        raise WeatherError('Invalid village coordinates.') from None


def _place_key(value):
    value = unicodedata.normalize('NFKC', value).casefold()
    return ''.join(char for char in value if char.isalnum() or unicodedata.category(char).startswith('M'))


def _state_key(value):
    key = _place_key(value)
    return {'orissa':'odisha', 'uttaranchal':'uttarakhand', 'pondicherry':'puducherry',
            'nctofdelhi':'delhi', 'nationalcapitalterritoryofdelhi':'delhi',
            'jammuandkashmir':'jammukashmir', 'andamanandnicobarislands':'andamannicobarislands'}.get(key,key)


def _distance_km(first, second):
    lat1,lon1 = map(math.radians,first)
    lat2,lon2 = map(math.radians,second)
    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371 * 2 * math.asin(min(1,math.sqrt(a)))


def village_coordinates(village, district='', state=''):
    """Resolve an Indian village without substituting a district forecast.

    Direct geocoding supports a country filter, but Indian states are filtered
    from the response (the API's state-code parameter is US-only). District is
    retained in the cache identity. The API does not provide district boundaries,
    so distant matches within a state are rejected rather than guessed. Nearby
    records within a two-kilometre area are treated as one village cluster.
    """
    if not settings.OPENWEATHER_API_KEY:
        raise WeatherError('OPENWEATHER_API_KEY is not configured on the server.')
    village, district, state = (value.strip() for value in (village,district,state))
    if not village:
        raise WeatherError('A village is required.')
    identity = '\0'.join(_place_key(value) for value in (village,district,state))
    key = 'owm:village:v2:' + hashlib.sha256(identity.encode()).hexdigest()
    if (cached := cache.get(key)) is not None:
        return cached
    canonical = VILLAGE_ALIASES.get((_state_key(state), _place_key(village)), village)
    try:
        response = requests.get(GEOCODING_URL,
            params={'q':f'{canonical},IN','limit':5,'appid':settings.OPENWEATHER_API_KEY}, timeout=10)
        if response.status_code != 200:
            raise WeatherError('Village lookup is unavailable.')
        payload = response.json()
        if not isinstance(payload,list):
            raise WeatherError('Invalid village lookup response.')
    except (requests.RequestException,ValueError):
        raise WeatherError('Village lookup is unavailable.') from None
    matches = {}
    for item in payload:
        if not isinstance(item,dict) or item.get('country') != 'IN':
            continue
        if state and _state_key(str(item.get('state',''))) != _state_key(state):
            continue
        names = [item.get('name','')]
        if isinstance(item.get('local_names'),dict):
            names.extend(item['local_names'].values())
        if not any(isinstance(name,str) and _place_key(name) == _place_key(canonical) for name in names):
            continue
        try:
            lat,lon = _coordinates(item.get('lat'),item.get('lon'))
        except WeatherError:
            continue
        matches[(round(lat,5),round(lon,5))] = (lat,lon)
    points = list(matches.values())
    if not points or any(_distance_km(a,b) > 2 for i,a in enumerate(points) for b in points[i+1:]):
        raise WeatherError('The village was not found or its name is ambiguous.')
    # Boundary centres and locality points can describe the same village. A
    # compact cluster is one village area; distant homonyms remain ambiguous.
    coordinates = (sum(lat for lat,lon in points)/len(points),
                   sum(lon for lat,lon in points)/len(points))
    cache.set(key,coordinates,24*60*60)
    return coordinates


def fetch_village_forecast(village, district='', state=''):
    latitude,longitude = village_coordinates(village,district,state)
    return fetch_forecast(village,latitude=latitude,longitude=longitude)


def summarize(payload):
    """Collapse OpenWeatherMap 3-hourly entries into per-day summaries."""
    zone = timezone(timedelta(seconds=payload.get('city', {}).get('timezone', 19800)))
    buckets = defaultdict(list)
    for item in payload.get('list', []):
        buckets[datetime.fromtimestamp(item['dt'], zone).date()].append(item)

    days = []
    for day, items in sorted(buckets.items()):
        days.append({
            'date': day.isoformat(),
            'city': payload.get('city', {}).get('name', ''),
            'slots': [{
                'time': datetime.fromtimestamp(i['dt'], zone).isoformat(),
                'temp': i['main'].get('temp'), 'humidity': i['main'].get('humidity'),
                'wind': i.get('wind', {}).get('speed'), 'gust': i.get('wind', {}).get('gust'),
                'rain': i.get('rain', {}).get('3h', 0), 'pop': i.get('pop'),
                'description': i.get('weather', [{}])[0].get('description',''),
                'code': i.get('weather', [{}])[0].get('id'),
                'daylight': i.get('sys', {}).get('pod') == 'd',
            } for i in sorted(items, key=lambda entry: entry['dt'])],
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
            notes.append(('warning', _("Soil moisture is low (%(soil_moisture)s%%) and little rain is expected. Irrigate in the next 24 hours, preferably early morning or evening.") % {'soil_moisture': soil_moisture}))
        elif soil_moisture < 25:
            notes.append(('info', _("Soil moisture is low (%(soil_moisture)s%%) but about %(rain_next3)s mm rain is forecast in 3 days. Consider a light irrigation only if crops are wilting.") % {'soil_moisture': soil_moisture, 'rain_next3': format(rain_next3, ".0f")}))
        elif soil_moisture > 60:
            notes.append(('info', _("Soil moisture is high (%(soil_moisture)s%%). Skip irrigation and ensure field drainage.") % {'soil_moisture': soil_moisture}))
        else:
            notes.append(('success', _("Soil moisture (%(soil_moisture)s%%) is adequate. No irrigation needed today.") % {'soil_moisture': soil_moisture}))

    if rain_next3 >= 20:
        notes.append(('warning', _("Heavy rain (~%(rain_next3)s mm) expected in the next 3 days. Postpone irrigation, fertilizer top-dressing and pesticide sprays; clear field drainage channels.") % {'rain_next3': format(rain_next3, ".0f")}))
    elif rain_next3 >= 5:
        notes.append(('info', _("Moderate rain (~%(rain_next3)s mm) expected. Plan sprays for dry windows so they are not washed off.") % {'rain_next3': format(rain_next3, ".0f")}))
    elif soil_moisture is None:
        notes.append(('info', _('Little rain expected in the next 3 days. Check soil moisture and irrigate if the top 5 cm of soil is dry.')))

    if max(d['temp_max'] for d in next3) >= 38:
        notes.append(('warning', _('High temperatures (38 °C+) expected. Irrigate in the evening, mulch to conserve moisture, and protect nursery seedlings and livestock from heat.')))
    if min(d['temp_min'] for d in next3) <= 4:
        notes.append(('warning', _('Frost risk: near-freezing nights expected. Give a light irrigation in the evening and cover sensitive seedlings.')))
    if sum(d['humidity'] for d in next3) / len(next3) >= 85:
        notes.append(('warning', _('Sustained high humidity favours fungal diseases (blight, mildew, blast). Scout fields closely and consider a preventive fungicide spray.')))
    if max(d['wind_speed'] for d in next3) >= 8:
        notes.append(('info', _('Strong winds expected. Avoid spraying pesticides (drift risk) and stake tall crops.')))
    return notes
