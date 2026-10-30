from functools import wraps
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse
from . import pests
from .models import PestEntry
from .pest_forms import PestEntryForm
from .pest_views import selection


def pest_admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_active or not request.user.profile.is_admin:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


@pest_admin_required
def index(request):
    context = selection(request)
    query = request.GET.get('q', '').strip()[:100]
    context.update({'entries': [r for r in pests.issues_for(context['crop'])
        if not query or query.casefold() in (r['name']+' '+r.get('symptoms', r['early'])).casefold()], 'query': query})
    return render(request, 'crops/pest_admin.html', context)


@pest_admin_required
def edit(request, crop_slug=None, issue_slug=None):
    if crop_slug:
        context = selection(request, crop_slug)
        row = next((r for r in pests.issues_for(context['crop']) if r['id'] == issue_slug), None)
        if row is None:
            from django.http import Http404
            raise Http404('Unknown crop issue')
        entry = PestEntry.objects.filter(crop_slug=crop_slug, issue_slug=issue_slug).first()
        if entry is None:
            entry = PestEntry(crop_slug=crop_slug, issue_slug=issue_slug, title=row['name'],
                kind=row['kind'], stages=[s['slug'] for s in row['stages']],
                symptoms=row['early']+'\n\n'+row['progress'],
                more_info=row['cause']+'\n\n'+row['conditions'],
                treat_now='\n\n'.join(row['management']))
    else:
        context = selection(request)
        entry = PestEntry(crop_slug=context['crop']['slug'])
    form = PestEntryForm(request.POST or None, request.FILES or None, instance=entry)
    if request.method == 'POST' and form.is_valid():
        entry = form.save(commit=False)
        entry.updated_by = request.user
        entry.save()
        messages.success(request, 'Saved to the crop library. The form is cleared and ready for your next entry.')
        return redirect(reverse('crops:pest_new', query={'crop': entry.crop_slug}))
    context.update({'form': form, 'entry': entry, 'editing': bool(issue_slug)})
    return render(request, 'crops/pest_edit.html', context)
