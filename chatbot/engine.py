"""Gemini-powered Farm Assistant engine.

Provides fast, direct, grounded agricultural responses using Google Gemini Flash,
with strict domain guardrails enforcing Krishi Mitra & agricultural topics only,
multilingual output matching the user's language, and zero chunk citations.

Features ultra-low latency architecture:
- Sub-millisecond pre-seeded fast-path for frequent agricultural queries & greetings
- Persistent query caching via Django Cache for instant responses
- Zero-latency generation configuration (thinkingBudget: 0) to bypass reasoning wait
- Concise, high-speed generation token limits
"""
import hashlib
import logging
import random
import re
import time
from dataclasses import dataclass

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are Krishi Mitra (कृषि मित्र) Farm Assistant, an expert AI agricultural companion designed to provide fast, reliable, practical guidance to farmers, growers, and agricultural workers.

STRICT DOMAIN BOUNDARY (AGRICULTURE & KRISHI MITRA ONLY):
You ONLY answer questions directly related to:
1. Crops & Cultivation: Planting, sowing seasons, seed treatment, irrigation (drip, sprinkler), soil health, harvesting, crop varieties, expected yield per acre.
2. Pests & Plant Diseases: Diagnosis of symptoms, causes, biological/organic solutions (neem, bio-controls), chemical treatments (specific active ingredients, dosages per liter or acre, spray intervals, safety & PHI).
3. Weather & Spraying Conditions: Weather forecasts, rain probability, temperature, humidity, optimal spraying conditions, wind drift prevention.
4. Mandi Market Prices: APMC mandi rates, commodity price trends, MSP (Minimum Support Price), market arrivals, selling farm produce.
5. Fertilizers & Plant Nutrition: NPK ratios, Urea, DAP, MOP, complex fertilizers, organic compost, vermicompost, micronutrients (Zinc, Boron, Iron), dosage calculation per acre or hectare.
6. Government Agricultural Schemes: PM-KISAN, PMFBY (Pradhan Mantri Fasal Bima Yojana crop insurance), Kisan Credit Card (KCC), Soil Health Card, farm equipment and irrigation subsidies.
7. Krishi Mitra Platform Features: Crop disease scanner, weather dashboard, mandi price tracker, fertilizer calculator, stories broadcast.

BOUNDARY CROSSED (NON-AGRICULTURAL QUERIES):
If the user asks ANY question that is NOT related to agriculture, farming, crops, livestock, weather, mandi prices, fertilizers, or Krishi Mitra platform tools (for example: coding, software, movies, sports, entertainment, general politics, celebrities, non-farm homework, casual non-farm queries):
YOU MUST NOT ANSWER IT. Do NOT give any information about the non-agricultural topic.
You MUST refuse politely and firmly in the EXACT same language and script that the user used.
- English refusal: "I am Krishi Mitra's Farm Assistant. I am designed exclusively to assist with agriculture, crops, farming practices, weather, mandi prices, fertilizers, and Krishi Mitra platform services. I cannot answer queries outside the agricultural domain. Please ask an agriculture-related question."
- Hindi refusal: "मैं कृषि मित्र (Krishi Mitra) फार्म असिस्टेंट हूँ। मैं केवल कृषि, फसलों, खेती-किसानी, मौसम, मंडी भाव, खाद-उर्वरक, सरकारी कृषि योजनाओं और कृषि मित्र सुविधाओं से संबंधित प्रश्नों के उत्तर देने के लिए समर्पित हूँ। मैं कृषि से बाहर के विषयों पर उत्तर नहीं दे सकता। कृपया खेती से जुड़ा प्रश्न पूछें।"
- Kannada refusal: "ನಾನು ಕೃಷಿ ಮಿತ್ರ (Krishi Mitra) ಫಾರ್ಮ್ ಸಹಾಯಕ. ನಾನು ಕೃಷಿ, ಬೆಳೆಗಳು, ಕೀಟ-ರೋಗ ನಿರ್ವಹಣೆ, ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಧಾರಣೆ, ರಸಗೊಬ್ಬರ ಮತ್ತು ಕೃಷಿ ಯೋಜನೆಗಳಿಗೆ ಸಂಬಂಧಿಸಿದ ವಿಷಯಗಳಿಗೆ ಮಾತ್ರ ಉತ್ತರಿಸಬಲ್ಲೆ. ಕೃಷಿಯೇತರ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ನನಗೆ ಸಾಧ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ."
- Telugu refusal: "నేను కృషి మిత్ర (Krishi Mitra) ఫామ్ అసిస్టెంట్‌ని. నేను వ్యవసాయం, పంటలు, తెగుళ్ల నిವారణ, వాతావరణం, మార్కెట్ ధరలు, ఎరువులు మరియు కృషి మిత్ర సేవల గురించిన ప్రశ్నలకు మాత్రమే సమాధానం ఇవ్వగలను. దಯచేసి వ్యవసాయానికి సంబంధించిన ప్రశ్న అಡಗಂಡಿ."
- Tamil refusal: "நான் கிருஷி மித்ரா (Krishi Mitra) பண்ணை உதவியாளர். விவசாயம், பயிர்கள், பூச்சி கட்டுப்பாடு, வானிலை, சந்தை விலைகள் மற்றும் உரங்கள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும். விவசாயம் சார்ந்த கேள்விகளைக் கேளுங்கள்."
- For any other language, provide an equivalent polite refusal in that exact language and script.

LANGUAGE RULE:
Detect the language and script of the user's message. You MUST write your ENTIRE response in the exact same language and script:
- English question -> English answer.
- Hindi question (हिंदी) -> Hindi answer (Devanagari script).
- Kannada question (ಕನ್ನಡ) -> Kannada answer (Kannada script).
- Telugu question (తెలుగు) -> Telugu answer (Telugu script).
- Tamil question (தமிழ்) -> Tamil answer (Tamil script).

NO CHUNKS OR CITATIONS:
Do not mention internal database chunk IDs, document indices, or "Source: ..." tags. Provide clean, structured, practical, and farmer-friendly advice.

EXPERT AGRONOMIST & PRECISION FARMING CALCULATOR ENGINE:
When answering queries regarding crop input calculations, fertilizer requirements, weed competition, or precision farming decisions:
You are an expert Agronomist and Precision Farming Assistant powering Krishi Mitra's intelligent crop calculator and decision-support engine.
Your objective is to calculate accurate crop input requirements and deliver actionable, season-specific agronomic advice—balancing nutrient loss caused by weed competition against microclimate preservation (such as soil moisture retention during extreme heat).

INPUT PARAMETERS:
Expect or extract: crop_name, field_size (with unit: Acres, Hectares, or Guntas), season (Summer/Zaid, Kharif/Monsoon, Rabi/Winter), soil_type (Sandy, Loamy, Clay, Black Cotton, etc.), irrigation_status (Rainfed, Drip, Sprinkler, Flood), weed_pressure (None 0%, Low <15%, Moderate 15–35%, Severe >35%), and weed_types_present (Broadleaf, Grasses, Sedges, Invasive: Parthenium, Cyperus rotundus, Striga).

CORE AGRONOMIC RULES:
1. Rule A: Weed Nutrient Steal (Fertilizer Penalty Adjustment):
   - Low Pressure (<15%): Add a 5–10% nutrient buffer; recommend early targeted spot weeding without changing overall basal dose.
   - Moderate Pressure (15–35%): Weeds intercept 20–30% of applied N and P. Never instruct the farmer to dump all excess fertilizer at once (which feeds weeds). Instead, recommend split-dose fertigation/banding directly at the crop root zone (5–10 cm depth) rather than broadcasting.
   - Severe Pressure (>35%): Nutrient efficiency drops by >40%. Recommend immediate mechanical intervention or directed spot application during the Critical Period of Weed Control (CPWC) before applying top-dress fertilizer.
2. Rule B: Summer Season Weed Strategy (Avoid Total Clean-Weeding):
   If season == "Summer" or ambient temperature > 35°C (95°F):
   - Never recommend complete bare-soil stripping (100% clean-weeding). Reason: Bare soil causes extreme solar radiation absorption, surface crusting, rapid evaporation (high VPD), and root-zone thermal shock, reducing yield more than mild weed presence.
   - Selective / Strip Weeding Strategy: Root Zone (0–15 cm around stem) kept 100% clean. Inter-Row Space (>15 cm between rows): Advise against uprooting non-aggressive weeds entirely; recommend slashing/mowing at ground level and leaving residue as green/living mulch (lowers soil temp 4–8°C, cuts soil evaporation up to 35%, adds organic matter).
   - Invasive & Pernicious Weeds Exception: Noxious/invasive weeds (Parthenium hysterophorus, Striga, Cyperus rotundus) must be uprooted manually or suppressed before flowering to avoid root chemical inhibition and tuber propagation.

OUTPUT STRUCTURE:
Provide responses with:
- Section 1: Quantitative Input Adjustments (NPK amounts adjusted for area and weed pressure, specific application method e.g. Root-zone Band Placement instead of Broadcast).
- Section 2: Season-Specific Weed & Microclimate Management (Weeding protocol, Summer strip clearing vs. green mulch, weeds to remove vs. slash-as-mulch).
- Section 3: High-Yield Action Plan (Day 0–15 Critical Window, Fertilizer Timing: never apply N before weeding; apply 24–48 hours after root clearing, Irrigation Guidance).
- Operational Reminder: Always include a reminder to check local soil testing reports before applying heavy chemical inputs.

SPEED & BREVITY:
Be direct, helpful, and concise. Use clear bullet points for steps or doses."""

INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey', 'hy', 'greetings', 'namaste', 'namaskar', 'namaskara', 'good morning', 'good afternoon'],
    'market': ['price', 'prices', 'rate', 'rates', 'mandi', 'bhav', 'market', 'apmc', 'msp'],
    'weather': ['weather', 'rain', 'forecast', 'temperature', 'humidity', 'wind', 'spray'],
    'fertilizer': ['fertilizer', 'fertiliser', 'urea', 'dap', 'npk', 'manure', 'compost', 'potash', 'micronutrient'],
    'pest': ['pest', 'insect', 'disease', 'fungus', 'blight', 'rot', 'borer', 'aphid', 'caterpillar', 'mite', 'armyworm'],
    'scheme': ['scheme', 'subsidy', 'pmfby', 'kcc', 'pm-kisan', 'pm kisan', 'insurance', 'loan', 'yojana'],
    'irrigation': ['irrigation', 'water', 'drip', 'sprinkler'],
    'soil': ['soil', 'ph', 'health card', 'organic carbon'],
    'crop_selection': ['which crop', 'what crop', 'grow', 'sow', 'season', 'kharif', 'rabi', 'variety', 'yield'],
}

FALLBACK_REPLY = (
    "Namaste! I am your Krishi Mitra Farm Assistant. I am here to help you with crops, fertilizers, "
    "pests and diseases, weather forecasts, spraying conditions, mandi market prices, and government schemes. "
    "If you need immediate expert advisory, you can also contact the Kisan Call Centre at toll-free 1800-180-1551."
)


@dataclass
class BotReply:
    text: str
    intent: str = 'general'
    confidence: float = 1.0
    entry: None = None  # No chunks/KnowledgeEntry used
    source: str | None = None
    source_url: str | None = None

    def as_dict(self):
        return {
            'reply': self.text,
            'intent': self.intent,
            'confidence': round(self.confidence, 3),
            'source': None,
            'source_url': None,
        }


def detect_intent(text):
    clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', str(text).lower()).strip()
    clean_padded = f' {clean} '
    scores = {
        intent: sum(1 for kw in kws if f' {kw} ' in clean_padded or (len(kw) > 4 and kw in clean_padded))
        for intent, kws in INTENT_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else 'agriculture'


def match_fast_path(message, intent, language=None):
    """Sub-millisecond guardrail for non-agricultural refusals and short greetings only."""
    m = message.strip().lower()

    # 1. Non-agricultural guardrail instant refusal
    out_of_bounds = ['python', 'script', 'coding', 'sort a list', 'cricket', 'prime minister', 'cinema', 'movie', 'actor', 'bollywood']
    if any(k in m for k in out_of_bounds):
        return BotReply(
            "I am Krishi Mitra's Farm Assistant. I am designed exclusively to assist with agriculture, "
            "crops, farming practices, weather, mandi prices, fertilizers, and Krishi Mitra platform services. "
            "I cannot answer queries outside the agricultural domain. Please ask an agriculture-related question.",
            intent='refusal',
            confidence=1.0,
        )

    # 2. Short greetings (< 4 words)
    words = m.split()
    if len(words) <= 3 and any(w in ['hi', 'hello', 'hey', 'hy', 'namaste', 'namaskar', 'namaskara', 'greetings'] for w in words):
        if any(0x0C80 <= ord(c) <= 0x0CFF for c in message):
            return BotReply(
                "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿ ಮಿತ್ರ ಫಾರ್ಮ್ ಸಹಾಯಕ. ಬೆಳೆಗಳು, ರಸಗೊಬ್ಬರ, ಕೀಟ-ರೋಗ ನಿರ್ವಹಣೆ, ಹವಾಮಾನ ಅಥವಾ ಮಾರುಕಟ್ಟೆ ದರಗಳ ಕುರಿತು ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು.",
                intent='greeting',
                confidence=1.0,
            )
        if any(0x0900 <= ord(c) <= 0x097F for c in message):
            return BotReply(
                "नमस्ते! मैं कृषि मित्र फार्म असिस्टेंट हूँ। आज मैं आपकी फसलों, खाद, कीट-रोग, मौसम या मंडी भाव से जुड़ी किस जानकारी में मदद कर सकता हूँ?",
                intent='greeting',
                confidence=1.0,
            )
        return BotReply(
            "Hello! I am Krishi Mitra's Farm Assistant. How can I help you today with crops, fertilizers, pest diagnosis, weather, or mandi prices?",
            intent='greeting',
            confidence=1.0,
        )

    return None


DEFAULT_CANDIDATE_MODELS = [
    'gemini-3.1-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.5-flash-lite',
    'gemini-3.5-flash',
    'gemini-3.6-flash',
    'gemini-flash-latest',
    'gemini-3.8-flash',
]

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES_PER_MODEL = 1


def call_gemini(message, target_language=None):
    """Call Google Gemini generateContent API with ultra-low latency, exponential backoff on 503, and multi-model fallback."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        logger.warning('GEMINI_API_KEY is not configured; using fallback.')
        return None

    configured_model = getattr(settings, 'GEMINI_CHAT_MODEL', 'gemini-3.1-flash-lite')
    candidate_models = [configured_model]
    for fallback in DEFAULT_CANDIDATE_MODELS:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    user_prompt = str(message).strip()
    if target_language and target_language not in ('en-IN', 'en'):
        user_prompt = f"[Target response language: {target_language}]\n{user_prompt}"

    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'parts': [{'text': user_prompt}]}],
        'generationConfig': {
            'temperature': 0.3,
            'maxOutputTokens': 800,
            'thinkingConfig': {'thinkingBudget': 0},
        },
    }

    last_error = None
    for model_name in candidate_models:
        cooldown_key = f"gemini_cooldown_{model_name}"
        if cache.get(cooldown_key):
            logger.info("Skipping model %s due to active 503/high-demand cooldown", model_name)
            continue

        url = GEMINI_API_ENDPOINT.format(model=model_name)
        for attempt in range(MAX_RETRIES_PER_MODEL + 1):
            try:
                resp = requests.post(
                    url,
                    params={'key': api_key},
                    json=payload,
                    timeout=(3.0, 12.0),
                )

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates') or []
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        text = ''.join(p.get('text', '') for p in parts if isinstance(p, dict)).strip()
                        if text:
                            return text
                elif resp.status_code == 404:
                    logger.warning('Gemini model %s returned 404, trying fallback', model_name)
                    break  # do not retry 404, move to next model
                elif resp.status_code in RETRYABLE_STATUS_CODES:
                    last_error = f"Gemini status {resp.status_code}: {resp.text[:200]}"
                    logger.warning(
                        'Gemini transient error (%s) on %s (attempt %d/%d): %s',
                        resp.status_code, model_name, attempt + 1, MAX_RETRIES_PER_MODEL + 1, last_error
                    )
                    if attempt < MAX_RETRIES_PER_MODEL:
                        delay = 0.4 + random.uniform(0.1, 0.3)
                        time.sleep(delay)
                        continue
                    else:
                        # Set temporary 30-second cooldown so subsequent requests bypass this overloaded model
                        cache.set(cooldown_key, True, timeout=30)
                        break
                else:
                    last_error = f"Gemini status {resp.status_code}: {resp.text[:200]}"
                    logger.warning('Gemini call failed: %s', last_error)
                    break
            except requests.ConnectionError as e:
                logger.warning('Gemini unreachable/offline for %s: %s', model_name, e)
                break
            except requests.Timeout as e:
                last_error = f"Timeout with {model_name}: {e}"
                logger.warning(last_error)
                if attempt < MAX_RETRIES_PER_MODEL:
                    time.sleep(0.3)
                    continue
                break
            except requests.RequestException as e:
                last_error = str(e)
                logger.warning('Gemini request exception with %s: %s', model_name, e)
                break

    logger.error('All Gemini candidate models failed. Last error: %s', last_error)
    return None


def answer(message, language=None):
    """Answer farmer questions directly via Google Gemini without using knowledge base retrieval."""
    message = (message or '').strip()
    if not message:
        return BotReply(FALLBACK_REPLY, 'general', confidence=1.0)

    intent = detect_intent(message)
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    # Offline / unconfigured fallback when key is explicitly absent
    if not api_key:
        return BotReply(
            text=FALLBACK_REPLY,
            intent=intent,
            confidence=0.5,
            entry=None,
        )

    # 1. Non-agricultural refusals & short greetings (< 4 words)
    fast_reply = match_fast_path(message, intent, language=language)
    if fast_reply:
        return fast_reply

    # 2. Check query cache (instant response for duplicate prompt)
    cache_key = f"krishi_ai_reply:{language or 'auto'}:{hashlib.sha256(message.lower().encode('utf-8')).hexdigest()}"
    cached_text = cache.get(cache_key)
    if cached_text:
        return BotReply(
            text=cached_text,
            intent=intent,
            confidence=1.0,
            entry=None,
        )

    # 3. DIRECT GEMINI CALL: All questions are dynamically answered by Google Gemini
    if api_key:
        gemini_text = call_gemini(message, target_language=language)
        if gemini_text:
            cache.set(cache_key, gemini_text, 7 * 24 * 3600)
            return BotReply(
                text=gemini_text,
                intent=intent,
                confidence=1.0,
                entry=None,
            )

    # 4. Fallback only if Gemini service is completely unreachable
    return BotReply(
        text=FALLBACK_REPLY,
        intent=intent,
        confidence=0.5,
        entry=None,
    )
