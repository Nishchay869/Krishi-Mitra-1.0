import json
import time
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import MarketFavourite
from .nearby import coordinates, identity


@login_required
@require_POST
def favourite(request):
    try:
        row = signing.loads(request.POST.get('token', ''), salt='market-favourite', max_age=30*86400)
        key = identity(row)
        if request.POST.get('action') not in ('add', 'remove'):
            raise ValueError
    except (signing.BadSignature, ValueError, KeyError, TypeError):
        return JsonResponse({'error':'Invalid market.'}, status=400)
    if request.POST['action'] == 'add':
        MarketFavourite.objects.get_or_create(user=request.user, identity=key, defaults={
            'name':row['name'], 'district':row['district_name'], 'state':row['state_name']})
    else:
        MarketFavourite.objects.filter(user=request.user, identity=key).delete()
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'favourite':request.POST['action'] == 'add'})
    next_url = request.POST.get('next', '')
    return redirect(next_url if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()) else 'market:prices')


@login_required
@require_POST
def location(request):
    try:
        data = json.loads(request.body)
        lat, lon = coordinates(data.get('latitude'), data.get('longitude'))
        label = str(data.get('label') or '').strip()[:200]
    except (ValueError, TypeError, AttributeError):
        return JsonResponse({'error':'Invalid location.'}, status=400)
    request.session['mandi_origin'] = {'lat':lat, 'lon':lon, 'label':label, 'saved_at':time.time()}
    return JsonResponse({'ok':True})
