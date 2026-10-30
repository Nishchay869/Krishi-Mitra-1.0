"""Distance filters use published market points, never district centres."""
import hashlib
import json
import math
import time
from functools import lru_cache
from pathlib import Path
from django.core import signing
from .provider import normalize, place_key

RADII = (50, 100, 200, 500)


def identity(row):
    values = (place_key(row['state_name']), place_key(row['district_name']), normalize(row['name']))
    return hashlib.sha256('\0'.join(values).encode()).hexdigest()


def coordinates(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
        if not (math.isfinite(lat) and math.isfinite(lon) and 6 <= lat <= 38 and 68 <= lon <= 98):
            raise ValueError
        return lat, lon
    except (ValueError, TypeError, OverflowError):
        raise ValueError('Invalid location.') from None


def distance_km(first, second):
    a, b = map(math.radians, first)
    c, d = map(math.radians, second)
    term = math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(term)))


@lru_cache(maxsize=1)
def market_points():
    data = json.loads((Path(__file__).parent/'data/coordinates.json').read_text())
    points = {}
    for item in data['markets']:
        key = identity({'state_name':item['state'], 'district_name':item['district'], 'name':item['name']})
        try:
            point = coordinates(item['latitude'], item['longitude'])
        except ValueError:
            continue
        # Conflicting published points are not silently substituted.
        if key in points and (points[key] is None or distance_km(points[key], point) > 2):
            points[key] = None
        else:
            points[key] = point
    return points


def origin(request):
    saved = request.session.get('mandi_origin', {})
    if isinstance(saved, dict) and time.time()-saved.get('saved_at', 0) < 3600:
        try:
            return coordinates(saved.get('lat'), saved.get('lon')), saved.get('label', '')
        except ValueError:
            pass
    if saved:
        request.session.pop('mandi_origin', None)
    profile = request.user.profile
    if not profile.village.strip():
        return None, ''
    from weather.services import village_coordinates, WeatherError
    try:
        point = village_coordinates(profile.village, profile.district, profile.state)
        return point, ', '.join(filter(None, [profile.village, profile.district, profile.state]))
    except WeatherError:
        return None, ''


def prepare(request, cards, connected):
    from .models import MarketFavourite
    point, label = origin(request) if connected and cards else (None, '')
    points = market_points() if connected and cards else {}
    favourites = set(MarketFavourite.objects.filter(user=request.user).values_list('identity', flat=True))
    for row in cards:
        row['identity'] = identity(row)
        row['favourite'] = row['identity'] in favourites
        row['favourite_token'] = signing.dumps({key:row[key] for key in ('name','district_name','state_name')}, salt='market-favourite')
        market_point = points.get(row['identity'])
        row['distance_km'] = distance_km(point, market_point) if point and market_point else None
        if market_point:
            row['map_url'] = 'https://www.google.com/maps/search/?api=1&query='+','.join(map(str,market_point))
    favourites_only = request.GET.get('favourites') == '1'
    candidates = [row for row in cards if not favourites_only or row['favourite']]
    def unique(rows):
        return len({r['identity'] for r in rows})
    counts = [{'radius':radius, 'count':unique(r for r in candidates if r['distance_km'] is not None and r['distance_km'] <= radius)} for radius in RADII]
    radius = request.GET.get('radius', 'all')
    radius = int(radius) if radius in {str(r) for r in RADII} else 'all'
    if point and radius != 'all':
        visible = [row for row in candidates if row['distance_km'] is not None and row['distance_km'] <= radius]
    else:
        visible = list(candidates)
    ordering = request.GET.get('sort', 'nearest' if point else 'latest')
    if ordering not in {'nearest','high','low','latest'}:
        ordering = 'latest'
    if ordering == 'nearest':
        visible.sort(key=lambda r:(r['distance_km'] is None, r['distance_km'] or 0, r['name']))
    elif ordering in {'high','low'}:
        visible.sort(key=lambda r:(r['modal_price'] is None, (-r['modal_price'] if ordering == 'high' else r['modal_price']) if r['modal_price'] is not None else 0, r['name']))
    priced = [r for r in visible if r['modal_price'] is not None]
    highest = max((r['modal_price'] for r in priced), default=None)
    nearest = min((r['distance_km'] for r in visible if r['distance_km'] is not None), default=None)
    for row in visible:
        row['highest'] = highest is not None and row['modal_price'] == highest
        row['nearest'] = nearest is not None and row['distance_km'] == nearest
    return {
        'cards':visible, 'nearby_origin':label, 'has_origin':bool(point), 'radius':radius,
        'radius_counts':counts, 'market_count':unique(visible), 'all_market_count':unique(candidates),
        'unknown_distance_count':unique(r for r in candidates if r['distance_km'] is None),
        'favourites_only':favourites_only, 'sort':ordering,
        'highlight':max(priced, key=lambda r:r['modal_price'], default=None),
        'distance_unavailable':radius != 'all' and not point,
    }
