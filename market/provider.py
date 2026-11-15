"""Official data.gov.in mandi observations; cached, bounded and never synthesized."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import re
import time

import logging

import requests
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.debug import sensitive_variables

logger = logging.getLogger(__name__)
ENDPOINT = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
SOURCE_URL = 'https://www.data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi'


class LocalPriceError(Exception):
    pass


class ProviderUnreachable(LocalPriceError):
    """The server cannot connect to data.gov.in at all (it refuses non-Indian servers such as
    Render's Singapore region). Farmers' browsers in India can still fetch it directly."""


BROWSER_SEED_SECONDS = 300
MAX_BROWSER_RECORDS = 1000


def _browser_cache_key(user_id, state, crop):
    return 'mandi:browser:' + hashlib.sha256(f'{user_id}|{state}|{crop}'.encode()).hexdigest()


def _summarize(records, truncated):
    """Latest observation per market/variety/grade; same-day conflicting prices are dropped."""
    latest = {}
    conflicts = set()
    for row in records:
        identity = (place_key(row['district_name']),normalize(row['name']),row['variety'],row['grade'])
        existing = latest.get(identity)
        if existing is None or row['date'] > existing['date']:
            latest[identity] = row
            conflicts.discard(identity)
        elif row['date'] == existing['date'] and any(row[k] != existing[k] for k in ('min_price','modal_price','max_price')):
            conflicts.add(identity)
    # Without a revision timestamp, two different prices for the same report
    # cannot be resolved safely by choosing whichever row arrived first.
    return {'rows':[r for key,r in latest.items() if key not in conflicts],
            'truncated':truncated, 'conflicts':len(conflicts), 'fetched_at':timezone.now()}


def seed_from_browser(user_id, state, crop, raw_records, truncated=False):
    """Store records the farmer's browser fetched from data.gov.in, for that farmer only.

    Every record goes through the same strict parse_record() checks (state/crop must match,
    no future dates, valid price units/ranges); nothing is shared with other users, so a
    tampered upload can only affect the uploader's own view. Returns the number of rows kept.
    """
    if not isinstance(raw_records, list) or len(raw_records) > MAX_BROWSER_RECORDS:
        raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
    rows = [r for r in (parse_record(raw, state, crop) for raw in raw_records if isinstance(raw, dict)) if r]
    cache.set(_browser_cache_key(user_id, state, crop), _summarize(rows, bool(truncated)), BROWSER_SEED_SECONDS)
    return len(rows)


def normalize(value):
    value = re.sub(r'\s+apmc\s*$', '', str(value).strip(), flags=re.I)
    return re.sub(r'[^\w]+', '', value.casefold())


def place_key(value):
    value = normalize(value)
    return {'bangalore':'bengaluru','bangalorerural':'bengalururural',
            'mysore':'mysuru','belgaum':'belagavi','shimoga':'shivamogga',
            'tumkur':'tumakuru','gulbarga':'kalaburagi','bijapur':'vijayapura'}.get(value,value)


def amount(value):
    try:
        number = Decimal(str(value).replace(',',''))
        return number if number.is_finite() and number >= 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def parse_record(raw, state, crop):
    # Do not trust the upstream filter silently returning a different state/crop.
    if normalize(raw.get('state','')) != normalize(state) or normalize(raw.get('commodity','')) != normalize(crop):
        return None
    if not str(raw.get('market') or '').strip() or not str(raw.get('district') or '').strip():
        return None
    try:
        day = datetime.strptime(raw['arrival_date'], '%d/%m/%Y').date()
    except (KeyError, TypeError, ValueError):
        return None
    if day > timezone.localdate():
        return None
    # This resource's documented price unit is INR per quintal. Never silently
    # divide a record declaring another price unit by 100.
    declared_unit = raw.get('price_unit')
    if declared_unit and normalize(declared_unit) not in {'rsquintal','rsperquintal','inrquintal','inrperquintal','quintal','rsqtl','inrqtl'}:
        return None
    prices = [amount(raw.get(key)) for key in ('min_price','modal_price','max_price')]
    if all(p is None for p in prices):
        return None
    lo, modal, hi = prices
    if ((lo is not None and hi is not None and lo > hi)
            or (modal is not None and lo is not None and modal < lo)
            or (modal is not None and hi is not None and modal > hi)):
        return None
    return {'name':str(raw['market']).strip(), 'district_name':str(raw['district']).strip(),
            'state_name':str(raw['state']).strip(),'commodity':str(raw['commodity']).strip(),
            'variety':str(raw.get('variety') or '').strip(),'grade':str(raw.get('grade') or '').strip(),
            'date':day,'min_price':lo,'modal_price':modal,'max_price':hi}


@sensitive_variables('api_key', 'params')
def fetch_local_prices(state, crop, user_id=None):
    api_key = settings.DATA_GOV_IN_API_KEY.strip()
    if not api_key:
        raise LocalPriceError('Live local prices are not connected yet.')
    identity = hashlib.sha256((api_key+'|'+state+'|'+crop).encode()).hexdigest()
    key = 'mandi:ogd:v2:'+identity
    cached = cache.get(key)
    if cached is not None:
        return cached
    if user_id is not None:
        seeded = cache.get(_browser_cache_key(user_id, state, crop))
        if seeded is not None:
            return seeded
    records, offset, total = [], 0, None
    deadline = time.monotonic()+30
    for _ in range(5):
        params = {'api-key':api_key,'format':'json','limit':200,'offset':offset,
                  'filters[state]':state,'filters[commodity]':crop}
        remaining = deadline-time.monotonic()
        if remaining < 1:
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
        started = time.monotonic()
        try:
            response = requests.get(ENDPOINT, params=params, headers={'User-Agent':'KrishiMitra/1.0'},
                                    timeout=(3,min(10,remaining)))
            response.raise_for_status()
            payload = response.json()
        except requests.HTTPError as exc:
            # Log only the status and the provider's own message: never the URL, it contains the API key.
            status = getattr(exc.response, 'status_code', '?')
            body = (getattr(exc.response, 'text', '') or '')[:200].replace(api_key, '<key>')
            logger.warning('data.gov.in mandi request failed: HTTP %s after %.1fs: %s', status, time.monotonic()-started, body)
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.') from None
        except (requests.RequestException, ValueError) as exc:
            logger.warning('data.gov.in mandi request failed: %s after %.1fs', type(exc).__name__, time.monotonic()-started)
            if isinstance(exc, (requests.ConnectionError, requests.ConnectTimeout)) and not isinstance(exc, requests.ReadTimeout):
                raise ProviderUnreachable('Market prices are unavailable right now. Please try again later.') from None
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.') from None
        if not isinstance(payload, dict) or payload.get('status') not in ('ok','success') or not isinstance(payload.get('records'),list):
            logger.warning('data.gov.in mandi response not usable: status=%r message=%r',
                           payload.get('status') if isinstance(payload, dict) else type(payload).__name__,
                           str(payload.get('message', ''))[:200].replace(api_key, '<key>') if isinstance(payload, dict) else '')
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
        batch = payload['records']
        try:
            total = int(payload['total'])
        except (KeyError, ValueError, TypeError):
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.') from None
        if total < 0:
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
        for raw in batch:
            row = parse_record(raw,state,crop) if isinstance(raw,dict) else None
            if row:
                records.append(row)
        offset += len(batch)
        if offset >= total:
            break
        if not batch:
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
    result = _summarize(records, offset < total)
    cache.set(key,result,300)
    return result
