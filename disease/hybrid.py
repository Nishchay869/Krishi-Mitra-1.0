"""Leaf diagnosis: Gemini first (any crop, field photos), local model as offline backup.

Gemini covers every crop and can reject non-leaf or unclear photos. When Gemini cannot be
used (no key, quota used up, no internet, timeout, bad response), the locally trained
model in ml/models answers instead, so the farmer still gets a result. Problems with the
photo itself are reported to the farmer and are not retried on the local model.
"""
import logging

from django.utils.translation import gettext as _

from . import gemini, predictor
from .gemini import DiagnosisError

logger = logging.getLogger(__name__)

# Photo problems: the farmer must retake the photo, the local model would not help.
PHOTO_ERRORS = {'invalid_image', 'image_quality', 'image_size'}


def analyze_leaf(image_file, crop='', location='', notes='', language='en'):
    try:
        return gemini.analyze_leaf(image_file, crop=crop, location=location, notes=notes, language=language)
    except DiagnosisError as exc:
        if exc.code in PHOTO_ERRORS:
            raise
        logger.warning('Gemini unavailable (%s), using local model: %s', exc.code, exc)
        reason = exc.code

    if hasattr(image_file, 'seek'):
        image_file.seek(0)
    result = predictor.predict(image_file, crop=crop, location=location, notes=notes, language=language)
    result['fallback_reason'] = reason
    note = _('Offline model used because the online AI was unavailable; please confirm with your local KVK.')
    result['summary'] = f"{note} {result.get('summary', '')}".strip()
    return result


__all__ = ['analyze_leaf', 'DiagnosisError']
