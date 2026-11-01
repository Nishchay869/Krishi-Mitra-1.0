"""Gemini-powered Farm Assistant engine.

Provides fast, direct, grounded agricultural responses using Google Gemini Flash,
with strict domain guardrails enforcing Krishi Mitra & agricultural topics only,
multilingual output matching the user's language, and zero chunk citations.
"""
import logging
import re
from dataclasses import dataclass

import requests
from django.conf import settings
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are Krishi Mitra (कृषि मित्र) Farm Assistant, an expert AI agricultural companion designed to provide fast, reliable, practical guidance to farmers, growers, and agricultural workers.

STRICT DOMAIN BOUNDARY (AGRICULTURE & KRISHI MITRA ONLY):
You ONLY answer questions directly related to:
1. Crops & Cultivation: Planting, sowing seasons, seed treatment, irrigation (drip, sprinkler), soil health, harvesting, crop varieties.
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
- Telugu refusal: "నేను కృషి మిత్ర (Krishi Mitra) ఫామ్ అసిస్టెంట్‌ని. నేను వ్యవసాయం, పంటలు, తెగుళ్ల నివారణ, వాతావరణం, మార్కెట్ ధరలు, ఎరువులు మరియు కృషి మిత్ర సేవల గురించిన ప్రశ్నలకు మాత్రమే సమాధానం ఇవ్వగలను. దయచేసి వ్యవసాయానికి సంబంధించిన ప్రశ్న అడగండి."
- Tamil refusal: "நான் கிருஷி மித்ரா (Krishi Mitra) பண்ணை உதவியாளர். விவசாயம், பயிர்கள், பூச்சி கட்டுப்பாடு, வானிலை, சந்தை விலைகள் மற்றும் உரங்கள் தொடர்பான கேள்விகளுக்கு மட்டுமே என்னால் பதிலளிக்க முடியும். விவசாயம் சார்ந்த கேள்விகளைக் கேளுங்கள்."
- For any other language (Marathi, Gujarati, Bengali, Punjabi, Malayalam, etc.), provide an equivalent polite refusal in that exact language and script.

LANGUAGE RULE:
Detect the language and script of the user's message. You MUST write your ENTIRE response in the exact same language and script:
- English question -> English answer.
- Hindi question (हिंदी) -> Hindi answer (Devanagari script).
- Kannada question (ಕನ್ನಡ) -> Kannada answer (Kannada script).
- Telugu question (తెలుగు) -> Telugu answer (Telugu script).
- Tamil question (தமிழ்) -> Tamil answer (Tamil script).
- Marathi question (मराठी) -> Marathi answer.
- Gujarati, Bengali, Punjabi, Malayalam, etc. -> In that exact language and script.
This language matching rule applies strictly to BOTH normal agricultural advice AND out-of-bounds refusals.

NO CHUNKS OR CITATIONS:
Do not mention internal database chunk IDs, document indices, or "Source: ..." tags. Provide clean, structured, practical, and farmer-friendly advice.

SPEED & BREVITY:
Be direct, helpful, and concise. Use clear bullet points for steps or doses."""

INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey', 'greetings', 'namaste', 'namaskar', 'namaskara', 'good morning'],
    'market': ['price', 'prices', 'rate', 'rates', 'mandi', 'bhav', 'market', 'apmc', 'msp'],
    'weather': ['weather', 'rain', 'forecast', 'temperature', 'humidity', 'wind', 'spray'],
    'fertilizer': ['fertilizer', 'fertiliser', 'urea', 'dap', 'npk', 'manure', 'compost', 'potash', 'micronutrient'],
    'pest': ['pest', 'insect', 'disease', 'fungus', 'blight', 'rot', 'borer', 'aphid', 'caterpillar', 'mite'],
    'scheme': ['scheme', 'subsidy', 'pmfby', 'kcc', 'pm-kisan', 'pm kisan', 'insurance', 'loan', 'yojana'],
    'irrigation': ['irrigation', 'water', 'drip', 'sprinkler'],
    'soil': ['soil', 'ph', 'health card', 'organic carbon'],
    'crop_selection': ['which crop', 'what crop', 'grow', 'sow', 'season', 'kharif', 'rabi', 'variety'],
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
            'source': None,  # All chunks removed
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


def call_gemini(message, target_language=None):
    """Call Google Gemini generateContent API for fast, grounded, multilingual farming answers."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        logger.warning('GEMINI_API_KEY is not configured; using fallback.')
        return None

    configured_model = getattr(settings, 'GEMINI_CHAT_MODEL', 'gemini-3.1-flash-lite')
    candidate_models = [configured_model]
    for fallback in ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.8-flash']:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    user_prompt = str(message).strip()
    if target_language and target_language not in ('en-IN', 'en'):
        user_prompt = f"[Target response language: {target_language}]\n{user_prompt}"

    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'parts': [{'text': user_prompt}]}],
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 800,
        },
    }

    last_error = None
    for model_name in candidate_models:
        url = GEMINI_API_ENDPOINT.format(model=model_name)
        try:
            resp = requests.post(
                url,
                params={'key': api_key},
                json=payload,
                timeout=(3, 15),
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
                continue
            else:
                last_error = f"Gemini status {resp.status_code}: {resp.text[:200]}"
                logger.warning('Gemini call failed: %s', last_error)
        except requests.ConnectionError as e:
            logger.warning('Gemini unreachable/offline: %s', e)
            break
        except requests.RequestException as e:
            last_error = str(e)
            logger.warning('Gemini request exception with %s: %s', model_name, e)
            continue

    logger.error('All Gemini candidate models failed. Last error: %s', last_error)
    return None


def answer(message, language=None):
    """Answer farmer questions using Gemini with domain guardrails and user-language responses."""
    message = (message or '').strip()
    if not message:
        return BotReply(FALLBACK_REPLY, 'general', confidence=1.0)

    intent = detect_intent(message)
    gemini_text = call_gemini(message, target_language=language)

    if gemini_text:
        return BotReply(
            text=gemini_text,
            intent=intent,
            confidence=1.0,
            entry=None,
        )

    # Offline / unconfigured fallback
    return BotReply(
        text=FALLBACK_REPLY,
        intent=intent,
        confidence=0.5,
        entry=None,
    )
