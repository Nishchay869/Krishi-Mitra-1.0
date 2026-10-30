"""Local mandi picker. Catalog metadata never substitutes for live price records."""
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .provider import fetch_local_prices, LocalPriceError, place_key, normalize, SOURCE_URL

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext as _


@lru_cache(maxsize=1)
def catalog():
    return json.loads((Path(__file__).parent/'data/catalog.json').read_text())


def choice(rows, value):
    return next((r for r in rows if str(r['id']) == str(value)), None)


def named(rows, name):
    return next((r for r in rows if r['name'].casefold() == name.strip().casefold()), None)


@login_required
def local_prices_page(request):
    data = catalog()
    states = sorted(data['states'], key=lambda r:r['name'])
    state = choice(states, request.GET.get('state')) if 'state' in request.GET else named(states, request.user.profile.state)
    districts = sorted([r for r in data['districts'] if state and r['state']==state['id']],key=lambda r:r['name'])
    district = choice(districts, request.GET.get('district')) if 'district' in request.GET else named(districts, request.user.profile.district)
    markets = sorted([r for r in data['markets'] if state and r['state']==state['id']
                      and (not district or r['district']==district['id'])],key=lambda r:r['name'])
    market = choice(markets, request.GET.get('market'))
    crops = sorted(data['crops'],key=lambda r:r['name'])
    saved = request.user.profile.selected_crops or []
    preferred = next((named(crops,c) for c in saved if named(crops,c)),None)
    crop = choice(crops, request.GET.get('crop')) if 'crop' in request.GET else (preferred or choice(crops,65))
    unit = 'kg' if request.GET.get('unit')=='kg' else 'qtl'
    live_connected = bool(settings.DATA_GOV_IN_API_KEY.strip())
    cards, error, truncated = [], None, False
    expanded_scope, reported_markets_url = False, None
    fetched_at, conflicts = None, 0
    if live_connected and state and crop:
        try:
            response = fetch_local_prices(state['name'],crop['name'])
            truncated = response['truncated']
            fetched_at = response.get('fetched_at')
            conflicts = response.get('conflicts',0)
            rows = response['rows']
            # Keep catalog locations selectable even when no observation exists today.
            # Add provider-only names instead of mapping them to a different location.
            for row in rows:
                if not any(place_key(d['name']) == place_key(row['district_name']) for d in districts):
                    districts.append({'id':row['district_name'],'name':row['district_name'],'state':state['id']})
            districts.sort(key=lambda r:r['name'])
            if request.GET.get('district') and district is None:
                district = choice(districts,request.GET['district'])
            scoped = [r for r in rows if not district or place_key(r['district_name'])==place_key(district['name'])]
            if (district and not scoped and rows and 'district' not in request.GET
                    and not request.GET.get('market')):
                district = None
                scoped = rows
                expanded_scope = True
            markets = sorted([r for r in data['markets'] if r['state']==state['id'] and
                              (not district or r['district']==district['id'])], key=lambda r:r['name'])
            for row in scoped:
                if not any(normalize(m['name'])==normalize(row['name']) for m in markets):
                    markets.append({'id':row['name'],'name':row['name'],'state':state['id'],
                                    'district':district['id'] if district else row['district_name']})
            markets.sort(key=lambda r:r['name'])
            market = choice(markets,request.GET.get('market'))
            # Invalid explicit location values must not broaden the requested search.
            invalid = ((bool(request.GET.get('district')) and district is None) or
                       (bool(request.GET.get('market')) and market is None))
            if not invalid:
                cards = [dict(r) for r in scoped if not market or normalize(r['name'])==normalize(market['name'])]
            if rows and not cards and (district or invalid or market):
                reported_markets_url = '?' + urlencode({
                    'state':state['id'], 'district':'', 'market':'',
                    'crop':crop['id'], 'unit':unit,
                })
            divisor = Decimal(100) if unit=='kg' else Decimal(1)
            for row in cards:
                row['source_prices'] = {key:row[key] for key in ('min_price','modal_price','max_price')}
                for key in ('min_price','modal_price','max_price'):
                    if row[key] is not None:
                        row[key] = row[key]/divisor
                row['days_old'] = max(0,(timezone.localdate()-row['date']).days)
            cards.sort(key=lambda r:(-r['date'].toordinal(),r['name'],r['variety']))
        except LocalPriceError as exc:
            error = str(exc)
    elif not live_connected:
        visible = [market] if market else markets[:6]
        for item in visible:
            place = choice(districts,item['district'])
            cards.append({**item,'district_name':place['name'] if place else '',
                          'state_name':state['name'],'min_price':None,'modal_price':None,
                          'max_price':None,'date':None})
    for row in cards:
        query = ', '.join(filter(None,[row['name'],row['district_name'],row['state_name'],'India']))
        row['map_url'] = 'https://www.google.com/maps/search/?'+urlencode({'api':1,'query':query})
    from .nearby import prepare
    nearby = prepare(request, cards, live_connected)
    favourite_query = request.GET.copy()
    favourite_query.update({'favourites':'0' if nearby['favourites_only'] else '1'})
    nearby['favourites_url'] = '?' + favourite_query.urlencode()
    return render(request,'market/local_prices.html',{
        'states':states,'districts':districts,'markets':markets,'crops':crops,
        'state':state,'district':district,'market':market,'crop':crop,'unit':unit,
        'cards':cards,'live_connected':live_connected,'error':error,'truncated':truncated,
        'expanded_scope':expanded_scope,'reported_markets_url':reported_markets_url,
        **nearby,
        'fetched_at':fetched_at,'conflicts':conflicts,
        'source_url':SOURCE_URL,'latest_date':max((c['date'] for c in nearby['cards'] if c.get('date')),default=None),
    })
