from django.utils.translation import gettext as _
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
            error = _('This tool is temporarily unavailable. Please try again later.')
    return render(request, 'crops/recommend.html', {'form': form, 'results': results, 'error': error})


@require_POST
def api_recommend(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)
    form = CropForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    try:
        return JsonResponse({'recommendations': _run(request, form.cleaned_data)})
    except ModelNotTrained as exc:
        return JsonResponse({'error': _('This tool is temporarily unavailable. Please try again later.')}, status=503)


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
        return render(request, 'crops/yield.html', {'error': _('This tool is temporarily unavailable. Please try again later.')})
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
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)
    try:
        bundle = load_bundle()
    except ModelNotTrained as exc:
        return JsonResponse({'error': _('This tool is temporarily unavailable. Please try again later.')}, status=503)
    form = YieldForm(payload, bundle=bundle)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse(_run_yield(request, form.cleaned_data))


def _fertilizer_context(request, data=None, params=None):
    from .fertilizer import calculate_fertilizer, calculate_tree_fertilizer, calculate_plant_fertilizer
    from .fertilizer_presets import PRESETS, preset_label
    from .forms import FertilizerForm
    from accounts.localization import ui_text

    params = params if params is not None else (data if data is not None else request.GET)
    planting_type = params.get('planting_type', 'plants')
    if planting_type not in ('plants', 'trees'):
        planting_type = 'plants'
    choices = {key: value for key, value in PRESETS.items() if value['mode'] == planting_type}
    saved = request.user.profile.selected_crops or []
    default = next((key for key, value in choices.items() if value['crop'] in saved), next(iter(choices)))
    selected = params.get('crop_preset', default)
    if selected not in choices:
        selected = default
    preset = choices[selected]
    initial = dict(zip(('nitrogen', 'phosphorus', 'potassium'), preset['rates']))
    initial.update(area_unit='acre', area=1, tree_count=1,
                   planting_type=planting_type, crop_preset=selected)
    form = FertilizerForm(data, planting_type=planting_type, preset=preset, initial=initial)
    result = None
    customized = False
    if data is not None and form.is_valid():
        inputs = form.cleaned_data.copy()
        mode = inputs.pop('planting_type')
        inputs.pop('crop_preset')
        customized = any(inputs[key] != rate for key, rate in zip(
            ('nitrogen', 'phosphorus', 'potassium'), preset['rates']))
        calculate = (calculate_tree_fertilizer if mode == 'trees' else
                     calculate_plant_fertilizer if preset.get('basis') == 'plant' else calculate_fertilizer)
        result = calculate(**inputs)
        for combination in result['combinations']:
            combination['title'] = '/'.join(ui_text(name) for name in combination['title'].split('/'))
    from .fertilizer_products import decorate_products, shop_context
    shops = shop_context(request.user.profile)
    decorate_products(result, shops['shop_location'])
    grouped = {}
    for key, value in choices.items():
        grouped.setdefault(ui_text(value['group']), []).append((key, preset_label(value)))
    return {
        'form': form, 'result': result, 'is_trees': planting_type == 'trees',
        'selected_preset': selected, 'preset': preset, 'preset_label': preset_label(preset),
        'preset_scope': ui_text(preset['scope']),
        'preset_choices': [(key, preset_label(value)) for key, value in choices.items()],
        'customized': customized, 'is_per_plant': preset.get('basis') == 'plant',
        'source_org': preset.get('source_org','TNAU'), 'source_region': preset.get('source_region','Tamil Nadu'),
        'per_unit_label': 'kg/tree' if planting_type == 'trees' else 'kg/pit' if preset.get('count_pits') else 'kg/plant' if preset.get('basis') == 'plant' else 'kg/ha',
        'preset_groups': list(grouped.items()), **shops,
    }


FERTILIZER_TOKEN_SALT = 'crops.fertilizer.application.v1'


def _load_fertilizer_calculation(request, token):
    from django.core import signing
    from django.http import Http404
    try:
        payload = signing.loads(token, salt=FERTILIZER_TOKEN_SALT, max_age=86400)
        if payload['user'] != request.user.pk or not isinstance(payload['inputs'], dict):
            raise ValueError
        return payload['inputs']
    except (signing.BadSignature, KeyError, ValueError, TypeError):
        raise Http404


def _fertilizer_links(request, context):
    from django.core import signing
    from django.urls import reverse
    from urllib.parse import urlencode
    if not context['result']:
        return
    data = {key: str(value) for key, value in context['form'].cleaned_data.items()}
    token = signing.dumps({'user': request.user.pk, 'inputs': data},
                         salt=FERTILIZER_TOKEN_SALT, compress=True)
    for combination in context['result']['combinations']:
        combination['application_url'] = reverse('crops:fertilizer_application',
            args=[combination['id']]) + '?' + urlencode({'calculation': token})


@login_required
def fertilizer_page(request):
    data = request.POST if request.method == 'POST' else None
    if request.method == 'GET' and request.GET.get('calculation'):
        data = _load_fertilizer_calculation(request, request.GET['calculation'])
    context = _fertilizer_context(request, data=data)
    _fertilizer_links(request, context)
    return render(request, 'crops/fertilizer.html', context)


@login_required
def fertilizer_application(request, combination):
    from django.http import Http404
    from django.urls import reverse
    from urllib.parse import urlencode
    from .fertilizer import COMBINATIONS
    from .fertilizer_application import application_stages
    if combination not in COMBINATIONS:
        raise Http404
    token = request.GET.get('calculation', '')
    data = _load_fertilizer_calculation(request, token)
    context = _fertilizer_context(request, data=data)
    if not context['result']:
        raise Http404
    selected = next(item for item in context['result']['combinations'] if item['id'] == combination)
    schedule = application_stages(context['selected_preset'], context['preset'],
        context['form'].cleaned_data, context['result'], combination, context['customized'])
    from .fertilizer_products import relevant_products
    context.update(combination=selected, schedule=schedule,
                   relevant_products=relevant_products(selected['products'], context['shop_location']),
                   back_url=reverse('crops:fertilizer') + '?' + urlencode({'calculation': token}))
    return render(request, 'crops/fertilizer_application.html', context)


@login_required
def fertilizer_shops(request):
    from django.http import HttpResponseBadRequest, HttpResponseRedirect
    from .fertilizer_products import shop_search_url
    location = request.GET.get('location', '').strip()
    if len(location) > 300:
        return HttpResponseBadRequest()
    return HttpResponseRedirect(shop_search_url(location))
