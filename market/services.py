"""Daily mandi prices from Agmarknet 2.0 (Directorate of Marketing & Inspection, GoI).

The public dashboard endpoint returns, per commodity, the average modal price (Rs/quintal)
across reporting mandis for the latest reported day and the two days before it, plus MSP.
Its own "trend" field does not match the prices, so the change is computed here.
"""
from datetime import date, datetime

import requests
from django.core.cache import cache

API_BASE = 'https://api.agmarknet.gov.in/v1/'
SOURCE = 'Agmarknet, Directorate of Marketing & Inspection, Govt. of India'
SOURCE_URL = 'https://agmarknet.gov.in/'
PRICE_CACHE_SECONDS = 30 * 60
STATES_CACHE_SECONDS = 24 * 60 * 60
ALL_INDIA_STATE_ID = 100000
# Agmarknet rejects the default python-requests User-Agent; identify the app honestly instead.
HEADERS = {'User-Agent': 'KrishiMitra/1.0 (agriculture assistant)'}


class MarketError(Exception):
    pass


def _request(method, path, **kwargs):
    try:
        resp = requests.request(method, API_BASE + path, headers=HEADERS, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketError('Market price service (Agmarknet) is unreachable right now. Please try again later.') from exc


def get_states():
    """[(state_id, state_name)] from Agmarknet, excluding the 'All States' pseudo-entry."""
    if (cached := cache.get('agmarknet:states')) is not None:
        return cached
    payload = _request('GET', 'daily-price-arrival/filters')
    states = sorted(
        ((s['state_id'], s['state_name'].strip()) for s in payload.get('data', {}).get('state_data', [])
         if s['state_id'] != ALL_INDIA_STATE_ID),
        key=lambda s: s[1],
    )
    cache.set('agmarknet:states', states, STATES_CACHE_SECONDS)
    return states


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_title_date(title):
    try:
        return datetime.strptime(title, '%d %b, %Y').date()
    except (TypeError, ValueError):
        return None


def compare(today, previous):
    """Return (direction, change, percent) where direction is up/down/same/na."""
    if today is None or previous is None or previous == 0:
        return 'na', None, None
    change = round(today - previous, 2)
    percent = round(change / previous * 100, 2)
    direction = 'up' if change > 0 else 'down' if change < 0 else 'same'
    return direction, change, percent


def parse(payload):
    data = payload.get('data') or {}
    price_cols = next((c['columns'] for c in data.get('columns', []) if c.get('key') == 'price_group'), [])
    dates = [_parse_title_date(c.get('title')) for c in price_cols] + [None, None]

    rows = []
    for rec in data.get('records', []):
        today, previous = _to_float(rec.get('as_on_price')), _to_float(rec.get('one_day_ago_price'))
        msp = _to_float(rec.get('msp_price'))
        direction, change, percent = compare(today, previous)
        rows.append({
            'commodity': rec.get('cmdt_name', '').strip(),
            'group': (rec.get('cmdt_grp_name') or 'Others').strip(),
            'price': today,
            'previous_price': previous,
            'two_days_ago_price': _to_float(rec.get('two_day_ago_price')),
            'change': change,
            'percent': percent,
            'direction': direction,
            'msp': msp,
            'vs_msp': None if msp is None or today is None else ('above' if today >= msp else 'below'),
            'arrival_tonnes': _to_float(rec.get('as_on_arrival')),
        })
    return {'date': dates[0], 'previous_date': dates[1], 'rows': rows}


def fetch_prices(state_id=None, on=None):
    """Latest prices (all-India when state_id is None) with previous-day comparison."""
    on = on or date.today()
    cache_key = f'agmarknet:prices:{state_id or "all"}:{on.isoformat()}'
    if (cached := cache.get(cache_key)) is not None:
        return cached

    body = {'dashboard': 'marketwise_price_arrival', 'date': on.isoformat(), 'format': 'json', 'page': 0}
    if state_id:
        body['state'] = int(state_id)
    payload = _request('POST', 'dashboard-data/', json=body)
    if payload.get('status') not in ('success', True):
        raise MarketError(payload.get('message') or 'No market data available.')

    result = parse(payload)
    cache.set(cache_key, result, PRICE_CACHE_SECONDS)
    return result
