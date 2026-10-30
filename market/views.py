from datetime import date
from django.utils.translation import gettext as _
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import SOURCE, SOURCE_URL, MarketError, fetch_prices, get_states


def _state_id(raw):
    try:
        return int(raw) or None
    except (TypeError, ValueError):
        return None


def _profile_state_id(user, states):
    name = user.profile.state.strip().lower()
    return next((sid for sid, sname in states if sname.lower() == name), None) if name else None


@login_required
def prices_page(request):
    states, data, error = [], None, None
    try:
        states = get_states()
        state_id = _state_id(request.GET.get('state')) if 'state' in request.GET else _profile_state_id(request.user, states)
        data = fetch_prices(state_id)
    except MarketError as exc:
        state_id, error = None, _(str(exc))

    groups, summary, days_old = [], {}, None
    if data:
        days_old = (date.today() - data['date']).days if data['date'] else None
        rows = sorted(data['rows'], key=lambda r: (r['group'], r['commodity']))
        groups = [(name, list(items)) for name, items in groupby(rows, key=lambda r: r['group'])]
        directions = [r['direction'] for r in data['rows']]
        summary = {'up': directions.count('up'), 'down': directions.count('down'),
                   'flat': directions.count('same') + directions.count('na')}
    return render(request, 'market/prices.html', {
        'states': states, 'state_id': state_id, 'state_name': dict(states).get(state_id, 'All India'),
        'data': data, 'groups': groups, 'summary': summary, 'error': error, 'days_old': days_old,
        'source': SOURCE, 'source_url': SOURCE_URL,
    })


def api_prices(request):
    try:
        data = fetch_prices(_state_id(request.GET.get('state')))
    except MarketError as exc:
        return JsonResponse({'error': str(exc)}, status=502)
    return JsonResponse({
        'date': data['date'].isoformat() if data['date'] else None,
        'days_old': (date.today() - data['date']).days if data['date'] else None,
        'previous_date': data['previous_date'].isoformat() if data['previous_date'] else None,
        'unit': 'Rs/quintal', 'source': SOURCE, 'prices': data['rows'],
    })
