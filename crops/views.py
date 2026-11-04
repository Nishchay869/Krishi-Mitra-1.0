from django.utils.translation import gettext as _
import json
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from accounts.models import PredictionLog

from .forms import CropForm, YieldForm
from .crop_metadata import REGIONAL_PRESETS
from .predictor import ModelNotTrained, recommend
from .yield_predictor import load_bundle, predict_yield


def _run(request, data, top_n=3):
    results = recommend(data, top_n=top_n)
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
            results = _run(request, form.cleaned_data, top_n=5)
        except ModelNotTrained as exc:
            error = _('This tool is temporarily unavailable. Please try again later.')
    return render(request, 'crops/recommend.html', {
        'form': form,
        'results': results,
        'error': error,
        'regional_presets': REGIONAL_PRESETS,
    })


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
        top_n = int(payload.get('top_n', 3))
        return JsonResponse({'recommendations': _run(request, form.cleaned_data, top_n=top_n)})
    except ModelNotTrained as exc:
        return JsonResponse({'error': _('This tool is temporarily unavailable. Please try again later.')}, status=503)


def _run_yield(request, data):
    result = predict_yield(**data)
    PredictionLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        kind=PredictionLog.KIND_YIELD, inputs=data, result=result,
    )
    return result


def yield_page(request):
    """Farming Calculator: Precision Agronomist Decision-Support Engine & Yield Planner."""
    bundle = None
    try:
        bundle = load_bundle()
    except Exception:
        bundle = None

    profile_state = ''
    user_crops = []
    if request.user.is_authenticated:
        try:
            profile = getattr(request.user, 'profile', None)
            if profile:
                profile_state = getattr(profile, 'state', '') or ''
                raw = getattr(profile, 'selected_crops', None)
                if raw is None and hasattr(profile, 'saved_crops'):
                    raw = [c.name for c in profile.saved_crops.all()]
                if raw:
                    user_crops = [c if isinstance(c, str) else getattr(c, 'name', str(c)) for c in raw]
        except Exception:
            pass

    if not user_crops:
        try:
            raw = request.session.get('farm_preferences', {}).get('selected_crops', [])
            user_crops = [c if isinstance(c, str) else str(c) for c in raw]
        except Exception:
            user_crops = []

    state = None
    if bundle and profile_state:
        state = next((st for st in bundle.get('states', []) if st.lower() == profile_state.lower().strip()), None)
    initial = {'state': state} if state else None

    form = None
    if bundle:
        form = YieldForm(request.POST or None, initial=initial, bundle=bundle)

    result = None
    agronomy_result = None

    if request.method == 'POST':
        if 'weed_pressure' in request.POST or 'field_size' in request.POST or 'crop_name' in request.POST:
            from .agronomy import calculate_precision_agronomy
            agronomy_result = calculate_precision_agronomy(
                crop_name=request.POST.get('crop_name', 'Maize'),
                field_size=float(request.POST.get('field_size', 1.0)),
                field_unit=request.POST.get('field_unit', 'Acre'),
                season=request.POST.get('season', 'Summer'),
                soil_type=request.POST.get('soil_type', 'Loamy'),
                irrigation_status=request.POST.get('irrigation_status', 'Drip'),
                weed_pressure=request.POST.get('weed_pressure', 'Low (<15%)'),
                weed_types_present=request.POST.getlist('weed_types_present') or request.POST.get('weed_types_present', '').split(','),
            )
        elif form and form.is_valid():
            result = _run_yield(request, form.cleaned_data)

    metrics = bundle['metrics']['time_2016_2020']['random_forest'] if bundle and 'metrics' in bundle else None
    latest_year = bundle.get('latest_year', '2020') if bundle else '2020'

    return render(request, 'crops/yield.html', {
        'form': form,
        'result': result,
        'agronomy_result': agronomy_result,
        'metrics': metrics,
        'latest_year': latest_year,
        'user_crops_json': json.dumps(user_crops),
        'user_state': profile_state,
    })


@require_POST
def api_yield(request):
    """JSON endpoint for yield prediction and precision agronomy calculations."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)

    # Check if this is a Precision Agronomy calculation request
    if any(k in payload for k in ('weed_pressure', 'field_size', 'weed_types_present', 'crop_name')) or (
        payload.get('action') == 'precision_agronomy'
    ):
        from .agronomy import calculate_precision_agronomy
        crop_name = payload.get('crop_name') or payload.get('crop') or 'Maize'
        field_size = float(payload.get('field_size') or payload.get('area') or payload.get('area_ha') or 1.0)
        field_unit = payload.get('field_unit') or payload.get('unit') or ('Hectare' if 'area_ha' in payload else 'Acre')
        season = payload.get('season') or 'Summer'
        soil_type = payload.get('soil_type') or 'Loamy'
        irrigation_status = payload.get('irrigation_status') or 'Drip'
        weed_pressure = payload.get('weed_pressure') or 'Moderate (15–35%)'
        weed_types = payload.get('weed_types_present') or payload.get('weed_types') or []

        assessment = calculate_precision_agronomy(
            crop_name=crop_name,
            field_size=field_size,
            field_unit=field_unit,
            season=season,
            soil_type=soil_type,
            irrigation_status=irrigation_status,
            weed_pressure=weed_pressure,
            weed_types_present=weed_types,
        )
        return JsonResponse(assessment.to_dict())

    # Fallback to legacy ML model prediction
    try:
        bundle = load_bundle()
    except ModelNotTrained as exc:
        return JsonResponse({'error': _('This tool is temporarily unavailable. Please try again later.')}, status=503)
    form = YieldForm(payload, bundle=bundle)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse(_run_yield(request, form.cleaned_data))


@require_POST
def api_agronomy(request):
    """Direct JSON API endpoint for the Precision Farming & Agronomist Decision Engine."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': _('Invalid JSON body.')}, status=400)

    from .agronomy import calculate_precision_agronomy
    assessment = calculate_precision_agronomy(
        crop_name=payload.get('crop_name') or payload.get('crop') or 'Maize',
        field_size=float(payload.get('field_size') or payload.get('area') or payload.get('area_ha') or 1.0),
        field_unit=payload.get('field_unit') or payload.get('unit') or 'Acre',
        season=payload.get('season') or 'Summer',
        soil_type=payload.get('soil_type') or 'Loamy',
        irrigation_status=payload.get('irrigation_status') or 'Drip',
        weed_pressure=payload.get('weed_pressure') or 'Moderate (15–35%)',
        weed_types_present=payload.get('weed_types_present') or payload.get('weed_types') or [],
    )
    return JsonResponse(assessment.to_dict())


def _fertilizer_context(request, data=None, params=None):
    from .fertilizer import calculate_fertilizer, calculate_tree_fertilizer, calculate_plant_fertilizer
    from .fertilizer_presets import get_effective_presets, preset_label
    from .forms import FertilizerForm
    from accounts.localization import ui_text

    params = params if params is not None else (data if data is not None else request.GET)
    planting_type = params.get('planting_type', 'plants')
    if planting_type not in ('plants', 'trees'):
        planting_type = 'plants'
    presets = get_effective_presets()
    choices = {key: value for key, value in presets.items() if value['mode'] == planting_type}
    profile = getattr(request.user, 'profile', None)
    saved = profile.selected_crops or [] if profile else []
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
    shops = shop_context(profile) if profile else {'shop_location': '', 'has_shop_location': False}
    decorate_products(result, shops['shop_location'])
    grouped = {}
    for key, value in choices.items():
        grouped.setdefault(ui_text(value['group']), []).append((key, preset_label(value)))

    is_admin = bool(request.user.is_authenticated and getattr(getattr(request.user, 'profile', None), 'is_admin', False))

    return {
        'form': form, 'result': result, 'is_trees': planting_type == 'trees',
        'selected_preset': selected, 'preset': preset, 'preset_label': preset_label(preset),
        'preset_scope': ui_text(preset['scope']),
        'preset_choices': [(key, preset_label(value)) for key, value in choices.items()],
        'customized': customized, 'is_per_plant': preset.get('basis') == 'plant',
        'source_org': preset.get('source_org','TNAU'), 'source_region': preset.get('source_region','Tamil Nadu'),
        'per_unit_label': 'kg/tree' if planting_type == 'trees' else 'kg/pit' if preset.get('count_pits') else 'kg/plant' if preset.get('basis') == 'plant' else 'kg/ha',
        'preset_groups': list(grouped.items()),
        'is_admin': is_admin,
        **shops,
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
    is_admin = bool(request.user.is_authenticated and getattr(getattr(request.user, 'profile', None), 'is_admin', False))
    if request.method == 'POST' and 'save_as_admin_default' in request.POST:
        if not is_admin:
            messages.error(request, _('Only administrators can update standard N-P-K preset rates.'))
            return redirect('crops:fertilizer')

        crop_preset = request.POST.get('crop_preset')
        planting_type = request.POST.get('planting_type', 'plants')
        from .fertilizer_presets import get_effective_presets
        from .models import FertilizerPreset
        presets = get_effective_presets()
        if not crop_preset or crop_preset not in presets:
            messages.error(request, _('Unknown crop preset selected.'))
            return redirect('crops:fertilizer')

        try:
            n_val = Decimal(request.POST.get('nitrogen', '0').strip())
            p_val = Decimal(request.POST.get('phosphorus', '0').strip())
            k_val = Decimal(request.POST.get('potassium', '0').strip())
            if n_val < 0 or p_val < 0 or k_val < 0:
                raise ValueError
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, _('Please enter valid non-negative numbers for N, P, and K.'))
            return redirect(f"{reverse('crops:fertilizer')}?crop_preset={crop_preset}&planting_type={planting_type}")

        preset_data = presets[crop_preset]
        preset_obj, created = FertilizerPreset.objects.get_or_create(
            preset_key=crop_preset,
            defaults={
                'crop_name': preset_data.get('crop', crop_preset.title()),
                'mode': preset_data.get('mode', planting_type),
                'nitrogen': n_val,
                'phosphorus': p_val,
                'potassium': k_val,
                'scope': preset_data.get('scope', ''),
                'source': preset_data.get('source', ''),
                'updated_by': request.user,
            }
        )
        if not created:
            preset_obj.nitrogen = n_val
            preset_obj.phosphorus = p_val
            preset_obj.potassium = k_val
            preset_obj.updated_by = request.user
            preset_obj.save()

        messages.success(
            request,
            _('Standard N-P-K rates for %(crop)s updated to N=%(n)s, P=%(p)s, K=%(k)s. All users will now see these rates as the default.') % {
                'crop': preset_obj.crop_name,
                'n': n_val,
                'p': p_val,
                'k': k_val,
            }
        )
        return redirect(f"{reverse('crops:fertilizer')}?crop_preset={crop_preset}&planting_type={planting_type}")

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


def _is_admin_user(user):
    return user.is_authenticated and getattr(getattr(user, 'profile', None), 'is_admin', False)


@user_passes_test(_is_admin_user, login_url='accounts:login')
def fertilizer_manage(request):
    """Admin dashboard to view, search, and update standard N-P-K nutrient rates for all crops."""
    from .models import FertilizerPreset
    from .fertilizer_presets import get_effective_presets
    presets = get_effective_presets()
    query = request.GET.get('q', '').strip().lower()
    mode_filter = request.GET.get('mode', 'all')

    db_map = {p.preset_key: p for p in FertilizerPreset.objects.select_related('updated_by').all()}

    items = []
    for key, p in presets.items():
        mode = p.get('mode', 'plants')
        crop = p.get('crop', key.title())
        scope = p.get('scope', '')
        if mode_filter in ('plants', 'trees') and mode != mode_filter:
            continue
        if query and query not in key.lower() and query not in crop.lower() and query not in scope.lower():
            continue
        db_obj = db_map.get(key)
        items.append({
            'key': key,
            'crop': crop,
            'mode': mode,
            'scope': scope,
            'rates': p['rates'],
            'db_obj': db_obj,
            'updated_at': db_obj.updated_at if db_obj else None,
            'updated_by': db_obj.updated_by if db_obj else None,
        })

    items.sort(key=lambda x: x['crop'])

    return render(request, 'crops/fertilizer_manage.html', {
        'items': items,
        'query': query,
        'mode_filter': mode_filter,
        'total_count': len(presets),
        'plants_count': sum(1 for p in presets.values() if p.get('mode') == 'plants'),
        'trees_count': sum(1 for p in presets.values() if p.get('mode') == 'trees'),
    })


@user_passes_test(_is_admin_user, login_url='accounts:login')
@require_POST
def fertilizer_preset_save(request):
    """Admin endpoint to update standard N-P-K preset values for a crop."""
    crop_preset = request.POST.get('preset_key', '').strip()
    from .fertilizer_presets import get_effective_presets
    from .models import FertilizerPreset
    presets = get_effective_presets()
    is_ajax = (request.headers.get('x-requested-with') == 'XMLHttpRequest' or
               'application/json' in request.headers.get('Accept', ''))

    if not crop_preset or crop_preset not in presets:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': _('Invalid crop preset selected.')}, status=400)
        messages.error(request, _('Invalid crop preset selected.'))
        return redirect('crops:fertilizer_manage')

    try:
        n_val = Decimal(request.POST.get('nitrogen', '0').strip())
        p_val = Decimal(request.POST.get('phosphorus', '0').strip())
        k_val = Decimal(request.POST.get('potassium', '0').strip())
        if n_val < 0 or p_val < 0 or k_val < 0:
            raise ValueError
    except (ValueError, TypeError, InvalidOperation):
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': _('Please provide valid non-negative numbers for N, P, and K.')}, status=400)
        messages.error(request, _('Please provide valid non-negative numbers for N, P, and K.'))
        return redirect('crops:fertilizer_manage')

    preset_data = presets[crop_preset]
    preset_obj, created = FertilizerPreset.objects.get_or_create(
        preset_key=crop_preset,
        defaults={
            'crop_name': preset_data.get('crop', crop_preset.title()),
            'mode': preset_data.get('mode', 'plants'),
            'nitrogen': n_val,
            'phosphorus': p_val,
            'potassium': k_val,
            'scope': preset_data.get('scope', ''),
            'source': preset_data.get('source', ''),
            'updated_by': request.user,
        }
    )
    if not created:
        preset_obj.nitrogen = n_val
        preset_obj.phosphorus = p_val
        preset_obj.potassium = k_val
        preset_obj.updated_by = request.user
        preset_obj.save()

    msg = _('Standard N-P-K rates for %(crop)s saved successfully! (N: %(n)s, P: %(p)s, K: %(k)s). All users will now see these updated rates.') % {
        'crop': preset_obj.crop_name,
        'n': n_val,
        'p': p_val,
        'k': k_val,
    }

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'message': msg,
            'crop_name': preset_obj.crop_name,
            'preset_key': preset_obj.preset_key,
            'rates': [float(n_val), float(p_val), float(k_val)],
            'updated_at': preset_obj.updated_at.strftime('%d %b, %H:%M'),
            'updated_by': request.user.username if request.user.is_authenticated else '',
        })

    messages.success(request, msg)
    next_url = request.POST.get('next') or reverse('crops:fertilizer_manage')
    return redirect(next_url)


def pesticide_calculator(request):
    """Interactive pesticide and spray dilution calculator matching farmer knapsack tanks."""
    user_crops = []
    try:
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                raw = getattr(profile, 'selected_crops', None)
                if raw is None and hasattr(profile, 'saved_crops'):
                    raw = [c.name for c in profile.saved_crops.all()]
                if raw:
                    user_crops = [c if isinstance(c, str) else getattr(c, 'name', str(c)) for c in raw]
    except Exception:
        user_crops = []

    if not user_crops:
        try:
            raw = request.session.get('farm_preferences', {}).get('selected_crops', [])
            user_crops = [c if isinstance(c, str) else str(c) for c in raw]
        except Exception:
            user_crops = []

    return render(request, 'crops/pesticide_calculator.html', {
        'user_crops_json': json.dumps(user_crops),
    })


@csrf_exempt
def api_crop_vision_diagnose(request):
    """
    Real-Time Plant Vision & IPM Advisory Diagnostic Endpoint.
    Accepts base64 video frame or image file, executes Laplacian blur rejection,
    CLAHE lighting normalization, multi-class segmentation, and returns
    digital pathology metrics, polygon boundaries, and IPM prescription.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)

    try:
        if request.content_type and 'application/json' in request.content_type:
            body = json.loads(request.body or '{}')
            frame_data = body.get('frame')
            target_hint = body.get('target_hint')
        else:
            frame_data = request.POST.get('frame')
            target_hint = request.POST.get('target_hint')
            if not frame_data and 'file' in request.FILES:
                frame_data = request.FILES['file'].read()

        if not frame_data:
            return JsonResponse({'success': False, 'error': 'No frame provided'}, status=400)

        from vision_engine import PlantVisionEngine
        engine = PlantVisionEngine()
        result = engine.analyze_frame(frame_data, target_hint=target_hint)
        return JsonResponse(result.model_dump())
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




