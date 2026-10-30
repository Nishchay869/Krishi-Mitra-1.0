"""Official data.gov.in mandi observations; cached, bounded and never synthesized."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import hashlib
import re
import time

import requests
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.debug import sensitive_variables

ENDPOINT = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
SOURCE_URL = 'https://www.data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi'


class LocalPriceError(Exception):
    pass


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
def fetch_local_prices(state, crop):
    api_key = settings.DATA_GOV_IN_API_KEY.strip()
    if not api_key:
        raise LocalPriceError('Live local prices are not connected yet.')
    identity = hashlib.sha256((api_key+'|'+state+'|'+crop).encode()).hexdigest()
    key = 'mandi:ogd:v2:'+identity
    cached = cache.get(key)
    if cached is not None:
        return cached
    records, offset, total = [], 0, None
    deadline = time.monotonic()+30
    for _ in range(5):
        params = {'api-key':api_key,'format':'json','limit':200,'offset':offset,
                  'filters[state]':state,'filters[commodity]':crop}
        remaining = deadline-time.monotonic()
        if remaining < 1:
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.')
        try:
            response = requests.get(ENDPOINT, params=params, headers={'User-Agent':'KrishiMitra/1.0'},
                                    timeout=(3,min(10,remaining)))
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            # Never propagate provider exception URLs: they contain the API key.
            raise LocalPriceError('Market prices are unavailable right now. Please try again later.') from None
        if not isinstance(payload, dict) or payload.get('status') not in ('ok','success') or not isinstance(payload.get('records'),list):
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
    # Keep each market/variety/grade's latest observation, without averaging varieties.
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
    result = {'rows':[r for key,r in latest.items() if key not in conflicts],
              'truncated':offset < total, 'conflicts':len(conflicts), 'fetched_at':timezone.now()}
    cache.set(key,result,300)
    return result
