import hashlib
import time

from django.core.cache import cache
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import PredictionLog

from .forms import LeafImageForm
from .gemini import DiagnosisError, analyze_leaf


def _run(request, cleaned):
    # Bound anonymous/API use of the external paid service as well as browser submissions.
    identity = str(request.user.pk) if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
    key = 'leaf-gemini:' + hashlib.sha256(identity.encode()).hexdigest() + ':' + str(int(time.time()) // 60)
    if cache.add(key, 1, timeout=70):
        count = 1
    else:
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=70)
            count = 1
    if count > 6:
        raise DiagnosisError(_('Too many photo requests. Please wait a minute before trying again.'), 'rate_limited', 429)
    image = cleaned['image']
    result = analyze_leaf(image, crop=cleaned.get('crop', ''),
                          location=cleaned.get('location', ''), notes=cleaned.get('notes', ''),
                          language=getattr(request, 'LANGUAGE_CODE', 'en'))
    PredictionLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        kind=PredictionLog.KIND_DISEASE, inputs={'filename': image.name, 'crop': cleaned.get('crop', ''), 'provider': 'gemini'}, result=result,
    )
    return result


@login_required
def detect_page(request):
    form = LeafImageForm(request.POST or None, request.FILES or None)
    result, error = None, None
    if request.method == 'POST' and form.is_valid():
        try:
            result = _run(request, form.cleaned_data)
        except DiagnosisError as exc:
            error = str(exc)
    return render(request, 'disease/detect.html', {'form': form, 'result': result, 'error': error})


@require_POST
def api_detect(request):
    form = LeafImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    try:
        return JsonResponse(_run(request, form.cleaned_data))
    except DiagnosisError as exc:
        return JsonResponse({'error': str(exc), 'code': exc.code}, status=exc.status)
