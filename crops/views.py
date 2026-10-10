import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import PredictionLog

from .forms import CropForm, YieldForm
from .predictor import ModelNotTrained, recommend
from .yield_predictor import load_bundle, predict_yield


def _run(request, data):
    results = recommend(data)
    PredictionLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        kind=PredictionLog.KIND_CROP, inputs=data, result={'top': results},
    )
    return results


@login_required
def recommend_page(request):
    form = CropForm(request.POST or None)
    results, error = None, None
    if request.method == 'POST' and form.is_valid():
        try:
            results = _run(request, form.cleaned_data)
        except ModelNotTrained as exc:
            error = str(exc)
    return render(request, 'crops/recommend.html', {'form': form, 'results': results, 'error': error})


@require_POST
def api_recommend(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    form = CropForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    try:
        return JsonResponse({'recommendations': _run(request, form.cleaned_data)})
    except ModelNotTrained as exc:
        return JsonResponse({'error': str(exc)}, status=503)


def _run_yield(request, data):
    result = predict_yield(**data)
    PredictionLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        kind=PredictionLog.KIND_YIELD, inputs=data, result=result,
    )
    return result


@login_required
def yield_page(request):
    try:
        bundle = load_bundle()
    except ModelNotTrained as exc:
        return render(request, 'crops/yield.html', {'error': str(exc)})
    profile_state = request.user.profile.state.strip().lower()
    state = next((st for st in bundle['states'] if st.lower() == profile_state), None)
    initial = {'state': state} if state else None
    form = YieldForm(request.POST or None, initial=initial, bundle=bundle)
    result = None
    if request.method == 'POST' and form.is_valid():
        result = _run_yield(request, form.cleaned_data)
    return render(request, 'crops/yield.html', {
        'form': form, 'result': result, 'metrics': bundle['metrics']['time_2016_2020']['random_forest'],
        'latest_year': bundle['latest_year'],
    })


@require_POST
def api_yield(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    try:
        bundle = load_bundle()
    except ModelNotTrained as exc:
        return JsonResponse({'error': str(exc)}, status=503)
    form = YieldForm(payload, bundle=bundle)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse(_run_yield(request, form.cleaned_data))
