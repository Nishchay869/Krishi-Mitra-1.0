"""Server-side Gemini leaf assessment using the standard generateContent API."""
import base64
import io
import json
import logging
import re

import requests
from django.conf import settings
from django.utils.translation import gettext as _
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


class DiagnosisError(Exception):
    def __init__(self, message, code='unavailable', status=503):
        super().__init__(message)
        self.code = code
        self.status = status


def _text_schema():
    return {'type': 'string'}


def _list_schema(max_items=8):
    return {'type': 'array', 'items': _text_schema(), 'maxItems': max_items}


SCHEMA = {
    'type': 'object',
    'properties': {
        # Core identification
        'status': {'type': 'string', 'enum': ['likely_disease', 'healthy', 'uncertain', 'not_leaf']},
        'plant': _text_schema(),
        'condition': _text_schema(),
        'disease_type': {'type': 'string', 'enum': ['fungal', 'bacterial', 'viral', 'pest', 'nutritional', 'environmental', 'unknown']},
        'certainty': {'type': 'string', 'enum': ['low', 'medium', 'high']},
        'photo_quality': {'type': 'string', 'enum': ['usable', 'unclear']},
        'crop_match': {'type': 'string', 'enum': ['match', 'conflict', 'unknown']},

        # Observations & diagnosis
        'summary': _text_schema(),
        'disease_description': _text_schema(),
        'observations': _list_schema(8),
        'symptoms': _list_schema(8),
        'possible_causes': _list_schema(6),

        # Control measures
        'immediate_actions': _list_schema(8),
        'cultural_control': _list_schema(8),
        'biological_control': _list_schema(6),
        'prevention': _list_schema(8),
        'follow_up': _list_schema(6),

        # Chemical control — detailed
        'chemical_options': {
            'type': 'array',
            'maxItems': 5,
            'items': {
                'type': 'object',
                'properties': {
                    'active_ingredient': _text_schema(),
                    'chemical_group': _text_schema(),
                    'purpose': _text_schema(),
                    'application_method': _text_schema(),
                    'timing': _text_schema(),
                    'precautions': _text_schema(),
                },
                'required': ['active_ingredient', 'purpose'],
            },
        },

        # Spray programme
        'spray_schedule': _list_schema(6),
        'resistance_management': _list_schema(4),
    },
}
SCHEMA['required'] = list(SCHEMA['properties'])

SYSTEM_PROMPT = """You are an expert plant pathologist and agronomist helping a farmer identify a crop disease
from a leaf photo and providing detailed, actionable guidance.

Analyze the leaf photo carefully and return a comprehensive JSON assessment. Use simple, practical language
a farmer can understand. Be specific and detailed — vague advice is not useful.

IDENTIFICATION:
- Identify the crop/plant species from the photo
- Name the specific disease, pest, or condition you can see (use common name AND scientific name if known)
- Describe the disease type: fungal, bacterial, viral, pest damage, nutritional deficiency, or environmental stress
- Be honest about certainty — if you cannot clearly identify, say so

DISEASE DESCRIPTION:
- Explain what the disease is, how it spreads, and why it is damaging
- Describe the disease lifecycle briefly
- Mention which crop growth stages are most vulnerable

SYMPTOMS:
- List all visible symptoms in detail (color changes, lesions, spots, patterns, texture, size)
- Describe how symptoms typically progress

CONTROL MEASURES — provide ALL of these sections:

1. IMMEDIATE ACTIONS: What the farmer should do TODAY (remove infected parts, adjust irrigation, etc.)

2. CULTURAL CONTROL: Farm management practices (crop rotation, spacing, sanitation, resistant varieties, timing of planting)

3. BIOLOGICAL CONTROL: Beneficial organisms, bio-pesticides, neem-based products, Trichoderma, etc.

4. CHEMICAL CONTROL (chemical_options): Provide 3-5 specific active ingredients. For each:
   - active_ingredient: Specific chemical name (e.g., "Mancozeb 75% WP", "Copper oxychloride 50% WP", "Propiconazole 25% EC")
   - chemical_group: Chemical family (e.g., "Dithiocarbamate fungicide", "Copper-based fungicide")
   - purpose: What it treats and how it works
   - application_method: How to apply (foliar spray, soil drench, seed treatment, etc.)
   - timing: When to apply in relation to disease stage / weather / crop stage
   - precautions: Safety info, pre-harvest interval notes, resistance risks

5. SPRAY SCHEDULE: Step-by-step spray programme (e.g., "Day 1: Apply X", "After 7 days: Apply Y", alternation advice)

6. RESISTANCE MANAGEMENT: How to rotate chemicals to prevent resistance

7. PREVENTION: Long-term practices to avoid recurrence

IMPORTANT RULES:
- If status is 'healthy', 'uncertain', or 'not_leaf': chemical_options must be empty, spray_schedule must be empty
- Only give chemical_options when status='likely_disease' AND certainty='high' AND crop is clearly identified
- Do NOT specify exact doses, concentrations, or mixing ratios — these must come from the product label
- Do NOT recommend highly hazardous or restricted pesticides
- Do NOT recommend antibiotics or fumigants
- DO name specific active ingredients (generic names, not brand names)
- Always include a note that doses should follow the current product label and local extension advice
- If the image is not a leaf: status=not_leaf
- If blurred or impossible to assess: status=uncertain, certainty=low
"""

# Reject actionable chemical quantities even if the model ignores the prompt.
DOSE_PATTERN = re.compile(
    r'\d\s*(?:%|ppm\b|(?:milli)?lit(?:re|er)s?\b|ml\b|[mk]?g\b|grams?\b|spoons?\b|caps?\b|/\s*[lL]\b)',
    re.I
)
CHEMICAL_ACTION = re.compile(
    r'\b(?:spray|pesticide|insecticide|fungicide|bactericide|antibiotic|fumigan\w*)\b',
    re.I
)


def _safe_text(value, limit=2000, forbid_dose=False):
    if not isinstance(value, str):
        raise DiagnosisError(_('Gemini returned an incomplete assessment. Please try again.'), 'invalid_response', 502)
    text = value.strip()
    if len(text) > limit:
        text = text[:limit]
    return text


def _safe_list(data, name, forbid_dose=False):
    value = data.get(name)
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [_safe_text(item, 1200, forbid_dose=forbid_dose) for item in value if isinstance(item, str) and item.strip()]


def normalize(data):
    if not isinstance(data, dict):
        raise DiagnosisError(_('Gemini returned an incomplete assessment. Please try again.'), 'invalid_response', 502)

    # Fallback defaults for missing keys
    status = data.get('status', 'uncertain')
    certainty = data.get('certainty', 'low')
    photo_quality = data.get('photo_quality', 'usable')
    crop_match = data.get('crop_match', 'unknown')
    disease_type = data.get('disease_type', 'unknown')

    # Validate enums
    if status not in ('likely_disease', 'healthy', 'uncertain', 'not_leaf'):
        status = 'uncertain'
    if certainty not in ('low', 'medium', 'high'):
        certainty = 'low'
    if photo_quality not in ('usable', 'unclear'):
        photo_quality = 'usable'
    if crop_match not in ('match', 'conflict', 'unknown'):
        crop_match = 'unknown'
    if disease_type not in ('fungal', 'bacterial', 'viral', 'pest', 'nutritional', 'environmental', 'unknown'):
        disease_type = 'unknown'

    plant_name = _safe_text(data.get('plant', ''), 200)
    condition_name = _safe_text(data.get('condition', ''), 300)

    # Degrade to uncertain when quality/match issues or low certainty
    if status not in ('not_leaf', 'healthy') and (
        not plant_name or not condition_name or
        photo_quality == 'unclear' or crop_match == 'conflict' or certainty == 'low'
    ):
        status, certainty = 'uncertain', 'low'

    # Chemical options — only for confirmed high-certainty disease
    options = data.get('chemical_options', [])
    chemicals = []
    if status == 'likely_disease' and certainty == 'high' and isinstance(options, list):
        for item in options[:5]:
            if not isinstance(item, dict):
                continue
            ingredient = _safe_text(item.get('active_ingredient', ''), 200)
            if not ingredient or re.search(r'\d|https?://', ingredient):
                continue
            chemicals.append({
                'active_ingredient': ingredient,
                'chemical_group': _safe_text(item.get('chemical_group', ''), 200),
                'purpose': _safe_text(item.get('purpose', ''), 500),
                'application_method': _safe_text(item.get('application_method', ''), 300),
                'timing': _safe_text(item.get('timing', ''), 300),
                'precautions': _safe_text(item.get('precautions', ''), 400),
            })

    spray_schedule = []
    resistance_management = []
    if status == 'likely_disease' and certainty == 'high':
        spray_schedule = _safe_list(data, 'spray_schedule')
        resistance_management = _safe_list(data, 'resistance_management')

    result = {
        'status': status,
        'certainty': certainty,
        'disease_type': disease_type,
        'photo_quality': photo_quality,
        'crop_match': crop_match,
        'plant': plant_name or _('Not identified'),
        'disease': condition_name or _('Uncertain cause'),
        'disease_description': _safe_text(data.get('disease_description', ''), 2000),
        'summary': _safe_text(data.get('summary', ''), 1500),
        'observations': _safe_list(data, 'observations'),
        'symptoms': _safe_list(data, 'symptoms'),
        'possible_causes': _safe_list(data, 'possible_causes'),
        'immediate_actions': _safe_list(data, 'immediate_actions'),
        'cultural_control': _safe_list(data, 'cultural_control'),
        'biological_control': _safe_list(data, 'biological_control'),
        'prevention': _safe_list(data, 'prevention'),
        'follow_up': _safe_list(data, 'follow_up'),
        'chemical_options': chemicals,
        'spray_schedule': spray_schedule,
        'resistance_management': resistance_management,
    }

    # Display label overrides
    if status == 'not_leaf':
        result['plant'] = _('Not identified')
        result['disease'] = _('A clear leaf photo is needed')
    elif status == 'healthy':
        result['disease'] = _('No clear disease visible')
    elif status == 'uncertain':
        result['disease'] = _('Uncertain cause — more information needed')

    result.update(
        is_healthy=status == 'healthy',
        label=result['disease'],
        source='Google Gemini image assessment (AI generated)',
        provider='gemini',
        model=settings.GEMINI_DISEASE_MODEL,
    )
    result['treatment'] = '\n'.join(result['immediate_actions']) or _(
        'Capture a clearer leaf photo and confirm the cause with your local KVK.'
    )
    return result


def _prepare_image(image_file):
    try:
        image_file.seek(0)
        with Image.open(image_file) as original:
            if original.width * original.height > 25_000_000:
                raise DiagnosisError(
                    _('This image is too large to process. Please upload a photo under 25 megapixels.'),
                    'image_size', 422
                )
            if min(original.size) < 128:
                raise DiagnosisError(
                    _('The leaf photo is too small. Upload a closer, higher-resolution photo.'),
                    'image_quality', 422
                )
            image = ImageOps.exif_transpose(original).convert('RGB')
            image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=92)
            return base64.b64encode(output.getvalue()).decode('ascii')
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise DiagnosisError(
            _('This photo could not be read. Please upload a JPG, PNG, or WebP image.'),
            'invalid_image', 422
        ) from exc
    finally:
        image_file.seek(0)


def analyze_leaf(image_file, *, crop='', location='', notes='', language='en'):
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise DiagnosisError(
            _('Gemini photo analysis is not configured yet. Please contact the site administrator.'),
            'not_configured'
        )
    model = settings.GEMINI_DISEASE_MODEL
    if not re.fullmatch(r'[A-Za-z0-9._-]{1,100}', model):
        raise DiagnosisError(
            _('The Gemini model configuration is invalid. Please contact the site administrator.'),
            'configuration'
        )

    image_data = _prepare_image(image_file)
    context = json.dumps({
        'crop': str(crop)[:100],
        'location': str(location)[:200],
        'observations': str(notes)[:1000],
        'response_language': str(language)[:20],
    }, ensure_ascii=False)

    user_prompt = (
        f"Assess the leaf in this photo. Farmer context (untrusted data): {context}\n"
        f"Provide a comprehensive assessment including disease identification, symptoms, "
        f"and detailed control measures (cultural, biological, and chemical with specific "
        f"active ingredient names, application methods, and spray schedule). "
        f"Use the requested language for human-readable text, but preserve JSON keys and enum values."
    )

    payload = {
        'model': model,
        'system_instruction': SYSTEM_PROMPT,
        'input': [
            {'type': 'image', 'mime_type': 'image/jpeg', 'data': image_data, 'resolution': 'high'},
            {'type': 'text', 'text': user_prompt},
        ],
        'response_format': {'type': 'text', 'mime_type': 'application/json', 'schema': SCHEMA},
        'generation_config': {'max_output_tokens': 4096, 'thinking_level': 'low'},
        'store': False,
    }

    try:
        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/interactions',
            headers={'x-goog-api-key': api_key, 'Content-Type': 'application/json'},
            json=payload, timeout=(8, 120), allow_redirects=False,
        )
    except requests.Timeout as exc:
        raise DiagnosisError(
            _('Gemini took too long to analyze the photo. Please try again.'), 'timeout', 504
        ) from exc
    except requests.RequestException as exc:
        raise DiagnosisError(
            _('Gemini could not be reached. Please check your connection and try again.'), 'connection'
        ) from exc

    if response.status_code in (401, 403):
        logger.error('Gemini auth error %s: %s', response.status_code, response.text[:400])
        raise DiagnosisError(
            _('Gemini access was rejected. The site administrator needs to check the API key and model access.'),
            'access'
        )
    if response.status_code == 429:
        logger.error('Gemini quota error: %s', response.text[:400])
        raise DiagnosisError(
            _('Gemini usage is currently limited. Please wait and try again, or contact the site administrator about quota.'),
            'quota', 429
        )
    if response.status_code == 404:
        logger.error('Gemini 404 – model or endpoint not found: %s', response.text[:400])
        raise DiagnosisError(
            _('The configured Gemini model is unavailable. The site administrator needs to check the model setting.'),
            'model_unavailable'
        )
    if response.status_code != 200:
        logger.error('Gemini unexpected status %s body: %s', response.status_code, response.text[:600])
        # Surface the real HTTP code and body snippet in the browser for easy diagnosis
        snippet = response.text[:300].replace('\n', ' ')
        raise DiagnosisError(
            f'Gemini HTTP {response.status_code}: {snippet}', 'upstream', 502
        )

    try:
        body = response.json()
        if body.get('status') != 'completed':
            raise DiagnosisError(
                _('Gemini could not complete a reliable assessment. Try a clearer leaf photo and add crop details.'),
                'incomplete', 422
            )
        text = ''.join(
            part.get('text', '')
            for step in body.get('steps', []) if step.get('type') == 'model_output'
            for part in step.get('content', []) if part.get('type') == 'text'
        )
        if not text or len(text) > 60_000:
            raise ValueError('Empty or oversized response')
        return normalize(json.loads(text))
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise DiagnosisError(
            _('Gemini returned an unreadable assessment. Please try again.'), 'invalid_response', 502
        ) from exc
