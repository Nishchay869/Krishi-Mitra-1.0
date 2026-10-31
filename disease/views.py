import hashlib
import json
import time
import uuid

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import PredictionLog

from .forms import LeafImageForm
from .predictor import DiagnosisError, predict as analyze_leaf


def _format_diagnosis(log):
    result = log.result or {}
    inputs = log.inputs or {}

    disease = result.get('disease') or result.get('label') or _('Confirm a diagnosis')
    plant = result.get('plant') or inputs.get('crop') or ''

    # Determine status: Complete or Incomplete (matching Plantix design)
    res_status = result.get('status')
    if (
        res_status in ('not_leaf', 'needs_confirmation', 'uncertain')
        or not result.get('disease')
        or result.get('disease') == 'Uncertain cause'
    ):
        disease = _('Confirm a diagnosis')
        status_label = _('Incomplete')
        status_type = 'incomplete'
    elif res_status in ('likely_disease', 'healthy'):
        status_label = _('Complete')
        status_type = 'complete'
    elif result.get('disease') or result.get('label'):
        status_label = _('Complete')
        status_type = 'complete'
    else:
        disease = _('Confirm a diagnosis')
        status_label = _('Incomplete')
        status_type = 'incomplete'

    image_url = inputs.get('image_url')
    if not image_url:
        image_url = '/static/images/crops/tomato.webp'

    created_at = log.created_at
    date_str = created_at.strftime('%d %b') if created_at else ''

    return {
        'id': log.id,
        'disease': disease,
        'plant': plant,
        'date': date_str,
        'status_label': str(status_label),
        'status_type': status_type,
        'image_url': image_url,
        'url': f'/disease/history/{log.id}/',
    }


def get_user_diagnoses(request, limit=None):
    """Retrieve formatted past diagnoses for current user or session."""
    if request.user.is_authenticated:
        qs = PredictionLog.objects.filter(user=request.user, kind=PredictionLog.KIND_DISEASE).order_by('-created_at')
    else:
        history_ids = request.session.get('diagnosis_history', [])
        if not history_ids:
            return []
        qs = PredictionLog.objects.filter(id__in=history_ids, kind=PredictionLog.KIND_DISEASE).order_by('-created_at')

    if limit:
        qs = qs[:limit]

    return [_format_diagnosis(log) for log in qs]


def _run(request, cleaned):
    # Bound anonymous/API use to protect server resources
    identity = str(request.user.pk) if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
    key = 'leaf-ml:' + hashlib.sha256(identity.encode()).hexdigest() + ':' + str(int(time.time()) // 60)
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

    image_url = ''
    saved_path = ''
    try:
        filename = f"diagnoses/{uuid.uuid4().hex[:12]}_{getattr(image, 'name', 'leaf.jpg')}"
        saved_path = default_storage.save(filename, image)
        image_url = default_storage.url(saved_path)
        if hasattr(image, 'seek'):
            image.seek(0)
    except Exception:
        image_url = ''
        saved_path = ''

    result = analyze_leaf(image, crop=cleaned.get('crop', ''),
                          location=cleaned.get('location', ''), notes=cleaned.get('notes', ''),
                          language=getattr(request, 'LANGUAGE_CODE', 'en'))

    inputs = {
        'filename': getattr(image, 'name', 'leaf.jpg'),
        'crop': cleaned.get('crop', ''),
        'location': cleaned.get('location', ''),
        'notes': cleaned.get('notes', ''),
        'image_url': image_url,
        'image_path': saved_path,
        'provider': result.get('provider', 'ml'),
    }

    user = getattr(request, 'user', None)
    authenticated_user = user if (user and getattr(user, 'is_authenticated', False)) else None

    log = PredictionLog.objects.create(
        user=authenticated_user,
        kind=PredictionLog.KIND_DISEASE,
        inputs=inputs,
        result=result,
    )

    log_id = getattr(log, 'id', None)
    if isinstance(log_id, int):
        if hasattr(request, 'session') and hasattr(request.session, 'get'):
            history = request.session.get('diagnosis_history', [])
            history.insert(0, log_id)
            request.session['diagnosis_history'] = history[:30]
            if hasattr(request.session, 'modified'):
                request.session.modified = True
        result['log_id'] = log_id

    if image_url:
        result['image_url'] = image_url

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


def history_page(request):
    """View all past diagnoses with batch and selected delete options."""
    diagnoses = get_user_diagnoses(request)
    return render(request, 'disease/history.html', {
        'diagnoses': diagnoses,
        'count': len(diagnoses),
    })


def history_detail(request, pk):
    """View a single saved diagnosis assessment."""
    if request.user.is_authenticated:
        log = get_object_or_404(PredictionLog, pk=pk, user=request.user, kind=PredictionLog.KIND_DISEASE)
    else:
        history_ids = request.session.get('diagnosis_history', [])
        if pk not in history_ids:
            raise Http404
        log = get_object_or_404(PredictionLog, pk=pk, kind=PredictionLog.KIND_DISEASE)

    result = log.result or {}
    inputs = log.inputs or {}
    image_url = inputs.get('image_url') or '/static/images/crops/tomato.webp'

    return render(request, 'disease/detail.html', {
        'log': log,
        'result': result,
        'inputs': inputs,
        'image_url': image_url,
    })


@require_POST
def delete_single(request, pk):
    """Delete a single diagnosis record and its stored photo."""
    if request.user.is_authenticated:
        log = get_object_or_404(PredictionLog, pk=pk, user=request.user, kind=PredictionLog.KIND_DISEASE)
    else:
        history_ids = request.session.get('diagnosis_history', [])
        if pk not in history_ids:
            raise Http404
        log = get_object_or_404(PredictionLog, pk=pk, kind=PredictionLog.KIND_DISEASE)

    img_path = (log.inputs or {}).get('image_path')
    if img_path and default_storage.exists(img_path):
        try:
            default_storage.delete(img_path)
        except Exception:
            pass
    log.delete()

    if not request.user.is_authenticated:
        request.session['diagnosis_history'] = [i for i in request.session.get('diagnosis_history', []) if i != pk]
        request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True})

    messages.success(request, _('Diagnosis record deleted.'))
    return redirect('disease:history')


@require_POST
def delete_selected(request):
    """Delete selected diagnosis records."""
    if not request.user.is_authenticated:
        history_ids = set(request.session.get('diagnosis_history', []))
    else:
        history_ids = None

    selected_ids = []
    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            selected_ids = body.get('selected_ids') or body.get('ids', [])
        except Exception:
            pass
    if not selected_ids:
        selected_ids = request.POST.getlist('selected_ids') or request.POST.getlist('ids')

    try:
        selected_ids = [int(i) for i in selected_ids if str(i).isdigit()]
    except (ValueError, TypeError):
        selected_ids = []

    if not selected_ids:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'error': _('No items selected for deletion.')}, status=400)
        messages.warning(request, _('No items selected for deletion.'))
        return redirect('disease:history')

    if request.user.is_authenticated:
        logs = PredictionLog.objects.filter(pk__in=selected_ids, user=request.user, kind=PredictionLog.KIND_DISEASE)
    else:
        valid_ids = [i for i in selected_ids if i in history_ids]
        logs = PredictionLog.objects.filter(pk__in=valid_ids, kind=PredictionLog.KIND_DISEASE)

    count = 0
    for log in logs:
        img_path = (log.inputs or {}).get('image_path')
        if img_path and default_storage.exists(img_path):
            try:
                default_storage.delete(img_path)
            except Exception:
                pass
        log.delete()
        count += 1

    if not request.user.is_authenticated and history_ids:
        request.session['diagnosis_history'] = [i for i in request.session.get('diagnosis_history', []) if i not in selected_ids]
        request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'deleted_count': count})

    messages.success(request, _('%(count)d diagnosis records deleted.') % {'count': count})
    return redirect('disease:history')


@require_POST
def delete_all(request):
    """Delete all diagnosis history for current user/session."""
    if request.user.is_authenticated:
        logs = PredictionLog.objects.filter(user=request.user, kind=PredictionLog.KIND_DISEASE)
    else:
        history_ids = request.session.get('diagnosis_history', [])
        logs = PredictionLog.objects.filter(pk__in=history_ids, kind=PredictionLog.KIND_DISEASE)

    count = 0
    for log in logs:
        img_path = (log.inputs or {}).get('image_path')
        if img_path and default_storage.exists(img_path):
            try:
                default_storage.delete(img_path)
            except Exception:
                pass
        log.delete()
        count += 1

    if not request.user.is_authenticated:
        request.session['diagnosis_history'] = []
        request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'deleted_count': count})

    messages.success(request, _('All diagnosis history has been deleted.'))
    return redirect('disease:history')

