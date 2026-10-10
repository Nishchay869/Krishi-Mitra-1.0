from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import PredictionLog

from .forms import LeafImageForm
from .predictor import ModelNotTrained, predict


def _run(request, image):
    result = predict(image)
    PredictionLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        kind=PredictionLog.KIND_DISEASE, inputs={'filename': image.name}, result=result,
    )
    return result


@login_required
def detect_page(request):
    form = LeafImageForm(request.POST or None, request.FILES or None)
    result, error = None, None
    if request.method == 'POST' and form.is_valid():
        try:
            result = _run(request, form.cleaned_data['image'])
        except ModelNotTrained as exc:
            error = str(exc)
    return render(request, 'disease/detect.html', {'form': form, 'result': result, 'error': error})


@require_POST
def api_detect(request):
    form = LeafImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    try:
        return JsonResponse(_run(request, form.cleaned_data['image']))
    except ModelNotTrained as exc:
        return JsonResponse({'error': str(exc)}, status=503)
