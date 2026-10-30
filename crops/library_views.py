from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext
from django.utils.text import slugify

from accounts.onboarding import CROP_GROUPS
from .library import catalog


def index(request):
    query = request.GET.get('q', '').strip()[:100]
    category = request.GET.get('category', '')
    groups = []
    for group, _ in CROP_GROUPS:
        if category and category != slugify(group):
            continue
        crops = [c for c in catalog() if c['group'] == group and
                 (not query or query.casefold() in (c['name'] + ' ' + gettext(c['name'])).casefold())]
        if crops:
            groups.append({'name': group, 'slug': slugify(group), 'crops': crops})
    return render(request, 'crops/library.html', {
        'groups': groups, 'query': query, 'category': category,
        'categories': [{'name': g, 'slug': slugify(g)} for g, _ in CROP_GROUPS],
        'count': sum(len(g['crops']) for g in groups),
    })


def detail(request, slug):
    crop = next((c for c in catalog() if c['slug'] == slug), None)
    if crop is None:
        raise Http404
    companions = [c for c in catalog() if c['name'] in crop['companions']]
    return render(request, 'crops/library_detail.html', {'crop': crop, 'companions': companions})
