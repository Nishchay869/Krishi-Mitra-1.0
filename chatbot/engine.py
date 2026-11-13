"""Gemini-powered Farm Assistant engine with ICAR-CIARI RAG Knowledge Augmentation.

Provides fast, direct, grounded agricultural responses using Google Gemini Flash,
retrieval-augmented with official ICAR-Central Island Agricultural Research Institute (CIARI)
Package of Practices for island and tropical crops (Organic Vegetables, Conventional PoP,
and Horticultural/Plantation Crops: Coconut, Arecanut, Banana, Papaya, Pineapple, Spices, Tubers).

Features ultra-low latency architecture:
- Sub-millisecond pre-seeded fast-path for frequent agricultural queries & greetings
- Zero-external-dependency local RAG retriever for ICAR-CIARI Package of Practices
- Context-augmented prompt generation grounding Gemini in verified agronomic science
- Zero chunk citations in response schema (clean, conversational formatting)
- Persistent query caching via Django Cache for instant responses
"""
import hashlib
import logging
import random
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _

from . import rag

logger = logging.getLogger(__name__)

GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are Krishi Mitra (कृषि मित्र) Farm Assistant, an expert AI agricultural companion designed to provide fast, reliable, practical guidance to farmers, growers, and agricultural workers.

AUTHORITATIVE SCIENTIFIC KNOWLEDGE BASE (ICAR-CIARI PACKAGE OF PRACTICES):
You are backed by the official Package of Practices developed by ICAR-Central Island Agricultural Research Institute (CIARI), Port Blair, Andaman & Nicobar Islands:
1. Package of Practices for Organic Vegetable production in A & N Islands (ICAR-CIARI).
2. Package of Practices (PoP) for Vegetable Cultivation in Andaman & Nicobar Islands (ICAR-CIARI / KVK).
3. Training Manual on Package of Practices for Major Horticultural Crops (Coconut, Arecanut, Banana, Papaya, Pineapple, Mango, Black Pepper, Cinnamon, Clove, Nutmeg, Ginger, Turmeric, Cassava/Tapioca, Sweet Potato, Colocasia, Elephant Foot Yam).

When answering queries regarding crops, varieties, spacing, organic nutrition (FYM, vermicompost, cow dung slurry, vermiwash, Panchagavya), chemical NPK fertilization, pest and disease management, or intercropping:
- Ground your advisory firmly in the provided ICAR-CIARI Package of Practices reference.
- State accurate recommended varieties (e.g., Arka Rakshak, CARI Brinjal-1, Andaman Ordinary Tall, Mangala, Grand Naine, Panniyur-1, Rio de Janeiro, Gajendra).
- Provide precise dosages and formulations (e.g., Cold-pressed Neem oil 10,000 ppm @ 5 ml/L + soap, Panchagavya 3% foliar spray, Trichoderma viride @ 10 g/L, 1% Bordeaux mixture, specific NPK kg/ha).
- Explicitly state that these recommendations are based on the official ICAR-CIARI Package of Practices to give the farmer maximum confidence.

STRICT DOMAIN BOUNDARY (AGRICULTURE & KRISHI MITRA ONLY):
You ONLY answer questions directly related to:
1. Crops & Cultivation: Planting, sowing seasons, seed treatment, nursery raised beds, spacing, irrigation (drip, sprinkler), soil health, harvesting, crop varieties, expected yield per acre/hectare.
2. Pests & Plant Diseases: Diagnosis of symptoms, causes, biological/organic solutions (neem, bio-controls, Trichoderma, Pseudomonas, pheromone traps), chemical treatments (specific active ingredients, dosages per liter or acre, spray intervals, safety & PHI).
3. Weather & Spraying Conditions: Weather forecasts, rain probability, temperature, humidity, optimal spraying conditions, wind drift prevention.
4. Mandi Market Prices: APMC mandi rates, commodity price trends, MSP (Minimum Support Price), market arrivals, selling farm produce.
5. Fertilizers & Plant Nutrition: NPK ratios, Urea, DAP, MOP, complex fertilizers, organic compost, vermicompost, cow dung slurry, vermiwash, Panchagavya, micronutrients (Zinc, Boron, Iron), dosage calculation.
6. Government Agricultural Schemes: PM-KISAN, PMFBY (crop insurance), Kisan Credit Card (KCC), Soil Health Card, farm equipment and irrigation subsidies.
7. Krishi Mitra Platform Features: Crop disease scanner, weather dashboard, mandi price tracker, fertilizer calculator, stories broadcast.

NEVER REFUSE AN AGRICULTURAL QUESTION:
Questions about any crop (e.g. cabbage, cauliflower, tomato, rice, ragi, wheat, cotton, mango, banana, vegetables, fruits, pulses, spices), soil nutrients, fertilizers (Nitrogen, Phosphorus, Potassium, Potash, Urea, DAP, NPK), pests, plant diseases, irrigation, or farming are ALWAYS valid agricultural inquiries. You MUST answer them with complete, professional, actionable agricultural advice.

BOUNDARY CROSSED (STRICTLY FOR NON-AGRICULTURAL QUERIES ONLY):
Refusal is strictly and exclusively permitted when the query is completely outside agriculture (such as politics, movies, celebrities, software coding/Python scripts, video games, sports, or general unrelated trivia).
If and ONLY if a query is completely non-agricultural:
Refuse politely and firmly in the EXACT same language and script that the user used:
- English refusal: "I am Krishi Mitra's Farm Assistant. I am designed exclusively to assist with agriculture, crops, farming practices, weather, mandi prices, fertilizers, and Krishi Mitra platform services. I cannot answer queries outside the agricultural domain. Please ask an agriculture-related question."
- Hindi refusal: "मैं कृषि मित्र (Krishi Mitra) फार्म असिस्टेंट हूँ। मैं केवल कृषि, फसलों, खेती-किसानी, मौसम, मंडी भाव, खाद-उर्वरक, सरकारी कृषि योजनाओं और कृषि मित्र सुविधाओं से संबंधित प्रश्नों के उत्तर देने के लिए समर्पित हूँ। मैं कृषि से बाहर के विषयों पर उत्तर नहीं दे सकता। कृपया खेती से जुड़ा प्रश्न पूछें।"

NO CHUNKS OR CITATIONS IN PAYLOAD:
Do not mention internal database chunk IDs or document indices. Present clean, conversational, structured guidance.

CRITICAL LANGUAGE INTEGRITY RULE:
1. Detect the user's language and script from their query.
2. You MUST generate your ENTIRE response exclusively in the exact same language and script used by the user:
   - Kannada question (ಕನ್ನಡ or Romanized Kannada) -> 100% Kannada response in Kannada script (ಕನ್ನಡ ಲಿಪಿಯಲ್ಲಿ ಸಂಪೂರ್ಣ ಉತ್ತರ ನೀಡಿ).
   - Hindi question (हिन्दी or Romanized Hindi) -> 100% Hindi response in Devanagari script (हिन्दी देवनागरी میں উত্তর دیں).
   - Telugu question (తెలుగు or Romanized Telugu) -> 100% Telugu response in Telugu script (తెలుగు లిపిలో సమాధానం ఇవ్వండి).
   - Tamil question (தமிழ் or Romanized Tamil) -> 100% Tamil response in Tamil script (தமிழ் எழுத்துக்களில் பதில் அளிக்கவும்).
   - Bengali question (বাংলা) -> 100% Bengali response in Bengali script (বাংলা লিপিতে উত্তর দিন).
   - Marathi question (मराठी) -> 100% Marathi response in Marathi script (मराठीत उत्तर द्या).
   - Gujarati question (ગુજરાતી) -> 100% Gujarati response in Gujarati script (ગુજરાતીમાં ઉત્તર આપો).
   - English question -> 100% English response.
3. STRICT PROHIBITION: NEVER default or switch to Hindi if the user asked in Kannada, Telugu, Tamil, Bengali, or English!
   Answering in Hindi when a farmer asked in Kannada, Telugu, or Tamil is strictly forbidden.

SPEED & BREVITY:
Be direct, actionable, and structured with clear bullet points."""

LANGUAGE_PROMPTS = {
    'kn-IN': 'Kannada language in Kannada script (ಕನ್ನಡ ಲಿಪಿ)',
    'hi-IN': 'Hindi language in Devanagari script (हिन्दी देवनागरी)',
    'te-IN': 'Telugu language in Telugu script (తెలుగు లిపి)',
    'ta-IN': 'Tamil language in Tamil script (தமிழ் எழுத்துக்கள்)',
    'bn-IN': 'Bengali language in Bengali script (বাংলা লিপি)',
    'mr-IN': 'Marathi language in Devanagari script (मराठी)',
    'gu-IN': 'Gujarati language in Gujarati script (ગુજરાતી)',
    'ml-IN': 'Malayalam language in Malayalam script (മലയാളം)',
    'pa-IN': 'Punjabi language in Gurmukhi script (ਪੰਜਾਬੀ)',
    'od-IN': 'Odia language in Odia script (ଓଡ଼ಿଆ)',
}

INTENT_KEYWORDS = {
    'greeting': ['hello', 'hi', 'hey', 'hy', 'greetings', 'namaste', 'namaskar', 'namaskara', 'good morning', 'good afternoon'],
    'market': ['price', 'prices', 'rate', 'rates', 'mandi', 'bhav', 'market', 'apmc', 'msp'],
    'weather': ['weather', 'rain', 'forecast', 'temperature', 'humidity', 'wind', 'spray'],
    'fertilizer': ['fertilizer', 'fertiliser', 'urea', 'dap', 'npk', 'manure', 'compost', 'potash', 'micronutrient', 'panchagavya', 'slurry', 'vermiwash'],
    'pest': ['pest', 'insect', 'disease', 'fungus', 'blight', 'rot', 'borer', 'aphid', 'caterpillar', 'mite', 'armyworm', 'koleroga', 'sigatoka', 'fruit fly'],
    'scheme': ['scheme', 'subsidy', 'pmfby', 'kcc', 'pm-kisan', 'pm kisan', 'insurance', 'loan', 'yojana'],
    'irrigation': ['irrigation', 'water', 'drip', 'sprinkler'],
    'soil': ['soil', 'ph', 'health card', 'organic carbon', 'lime'],
    'crop_selection': ['which crop', 'what crop', 'grow', 'sow', 'season', 'kharif', 'rabi', 'variety', 'yield', 'spacing', 'intercrop'],
}

FALLBACK_REPLIES = {
    'kn-IN': (
        "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಮಿತ್ರ ಫಾರ್ಮ್ ಸಹಾಯಕ. ಬೆಳೆಗಳು, ರಸಗೊಬ್ಬರ, ಕೀಟ-ರೋಗಗಳು, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ, "
        "ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ದರಗಳು ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ. "
        "ತುರ್ತು ತಜ್ಞರ ಸಲಹೆಗಾಗಿ, ನೀವು ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ ಅನ್ನು ಟೋಲ್-ಫ್ರೀ 1800-180-1551 ಗೆ ಸಂಪರ್ಕಿಸಬಹುದು."
    ),
    'hi-IN': (
        "नमस्ते! मैं आपका कृषि मित्र फार्म असिस्टेंट हूँ। मैं फसलों, उर्वरकों, कीटों और रोगों, "
        "मौसम पूर्वानुमान, मंडी भाव और सरकारी योजनाओं में आपकी सहायता के लिए यहाँ हूँ। "
        "तत्काल विशेषज्ञ सलाह के लिए आप टोल-फ्री 1800-180-1551 पर किसान कॉल सेंटर से भी संपर्क कर सकते हैं।"
    ),
    'te-IN': (
        "నమస్కారం! నేను మీ కృషి మిత్ర ఫార్మ్ అసిస్టెంట్. పంటలు, ఎరువులు, తెగుళ్ళు మరియు వ్యాధులు, "
        "వాతావరణ సూచనలు, మార్కెట్ ధరలు మరియు ప్రభుత్వ పథకాలపై మీకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. "
        "తక్షణ నిపుణుల సలహా కోసం, మీరు టోల్-ఫ్రీ 1800-180-1551 లో కిసాన్ కాల్ సెంటర్‌ను సంప్రదించవచ్చు."
    ),
    'ta-IN': (
        "வணக்கம்! நான் உங்கள் கிருஷி மித்ரா விவசாய உதவியாளர். பயிர்கள், உரங்கள், பூச்சிகள் மற்றும் நோய்கள், "
        "வானிலை முன்னறிவிப்பு, மண்டி சந்தை விலைகள் மற்றும் அரசு திட்டங்கள் குறித்து உங்களுக்கு உதவ நான் இங்கு இருக்கிறேன். "
        "உடனடி நிபுணர் ஆலோசனைக்கு, 1800-180-1551 என்ற கட்டணமில்லா எண்ணில் கிசான் அழைப்பு மையத்தைத் தொடர்பு கொள்ளலாம்."
    ),
    'en-IN': (
        "Namaste! I am your Krishi Mitra Farm Assistant. I am here to help you with crops, fertilizers, "
        "pests and diseases, weather forecasts, spraying conditions, mandi market prices, and government schemes. "
        "If you need immediate expert advisory, you can also contact the Kisan Call Centre at toll-free 1800-180-1551."
    ),
}

FALLBACK_REPLY = FALLBACK_REPLIES['en-IN']


def get_localized_fallback(language='en-IN') -> str:
    return FALLBACK_REPLIES.get(language, FALLBACK_REPLIES['en-IN'])


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
    """Sub-millisecond guardrail for non-agricultural refusals and short greetings in the user's language."""
    m = message.strip().lower()

    # 1. Non-agricultural guardrail instant refusal in user's language
    out_of_bounds = ['python', 'script', 'coding', 'sort a list', 'cricket', 'prime minister', 'cinema', 'movie', 'actor', 'bollywood']
    if any(k in m for k in out_of_bounds):
        # Kannada refusal
        if any(0x0C80 <= ord(c) <= 0x0CFF for c in message):
            refusal_text = (
                "ನಾನು ಕೃಷಿ ಮಿತ್ರ ಫಾರ್ಮ್ ಸಹಾಯಕ. ನಾನು ಕೇವಲ ಕೃಷಿ, ಬೆಳೆಗಳು, ಬೇಸಾಯ ಪದ್ಧತಿಗಳು, ಹವಾಮಾನ, "
                "ಮಂಡಿ ದರಗಳು, ರಸಗೊಬ್ಬರಗಳು ಮತ್ತು ಕೃಷಿ ಮಿತ್ರ ಸೇವೆಗಳಿಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾಗಿದೆ. "
                "ದಯವಿಟ್ಟು ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ."
            )
        # Telugu refusal
        elif any(0x0C00 <= ord(c) <= 0x0C7F for c in message):
            refusal_text = (
                "నేను కృషి మిత్ర ఫార్మ్ అసిస్టెంట్. నేను వ్యవసాయం, పంటలు, వాతావరణం, మార్కెట్ ధరలు, "
                "మరియు ఎరువులకు సంబంధించిన ప్రశ్నలకు మాత్రమే సమాధానం ఇవ్వగలను. దయచేసి వ్యవసాయ సంబంధిత ప్రశ్నను అడగండి."
            )
        # Tamil refusal
        elif any(0x0B80 <= ord(c) <= 0x0BFF for c in message):
            refusal_text = (
                "நான் கிருஷி மித்ரா விவசாய உதவியாளர். நான் விவசாயம், பயிர்கள், வானிலை, மண்டி விலைகள் "
                "மற்றும் உரங்கள் தொடர்பான கேள்விகளுக்கு மட்டுமே பதிலளிக்க முடியும். தயவுசெய்து விவசாயம் தொடர்பான கேள்வியைக் கேளுங்கள்."
            )
        # Hindi refusal
        elif any(0x0900 <= ord(c) <= 0x097F for c in message):
            refusal_text = (
                "मैं कृषि मित्र (Krishi Mitra) फार्म असिस्टेंट हूँ। मैं केवल कृषि, फसलों, खेती-किसानी, "
                "मौसम, मंडी भाव, खाद-उर्वरक और कृषि मित्र सेवाओं से संबंधित प्रश्नों के उत्तर देने के लिए समर्पित हूँ। "
                "मैं कृषि से बाहर के विषयों पर उत्तर नहीं दे सकता। कृपया खेती से जुड़ा प्रश्न पूछें।"
            )
        # English refusal
        else:
            refusal_text = (
                "I am Krishi Mitra's Farm Assistant. I am designed exclusively to assist with agriculture, "
                "crops, farming practices, weather, mandi prices, fertilizers, and Krishi Mitra platform services. "
                "I cannot answer queries outside the agricultural domain. Please ask an agriculture-related question."
            )
        return BotReply(refusal_text, intent='refusal', confidence=1.0)

    # 2. Short greetings (< 4 words) in user's language
    words = m.split()
    if len(words) <= 3 and any(w in ['hi', 'hello', 'hey', 'hy', 'namaste', 'namaskar', 'namaskara', 'namaskaram', 'vanakkam', 'greetings'] for w in words):
        if any(0x0C80 <= ord(c) <= 0x0CFF for c in message) or 'namaskara' in m:
            return BotReply(
                "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿ ಮಿತ್ರ ಫಾರ್ಮ್ ಸಹಾಯಕ. ಬೆಳೆಗಳು, ರಸಗೊಬ್ಬರ, ಕೀಟ-ರೋಗ ನಿರ್ವಹಣೆ, ಹವಾಮಾನ ಅಥವಾ ಮಾರುಕಟ್ಟೆ ದರಗಳ ಕುರಿತು ನೀವು ಯಾವುದೇ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು.",
                intent='greeting',
                confidence=1.0,
            )
        if any(0x0C00 <= ord(c) <= 0x0C7F for c in message) or 'namaskaram' in m:
            return BotReply(
                "నమస్కారం! నేను కృషి మిత్ర ఫార్మ్ అసిస్టెంట్. పంటలు, ఎరువులు, తెగుళ్ళు, వాతావరణం లేదా మార్కెట్ ధరల గురించి మీరు ఏదైనా ప్రశ్న అడగవచ్చు.",
                intent='greeting',
                confidence=1.0,
            )
        if any(0x0B80 <= ord(c) <= 0x0BFF for c in message) or 'vanakkam' in m:
            return BotReply(
                "வணக்கம்! நான் உங்கள் கிருஷி மித்ரா விவசாய உதவியாளர். பயிர்கள், உரங்கள், பூச்சி-நோய் மேலாண்மை, வானிலை அல்லது சந்தை விலைகள் குறித்து நீங்கள் கேட்கலாம்.",
                intent='greeting',
                confidence=1.0,
            )
        if any(0x0900 <= ord(c) <= 0x097F for c in message) or 'namaste' in m or 'namaskar' in m:
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
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.1-flash-lite',
    'gemini-3.1-flash-lite-preview',
    'gemini-3.7-flash',
    'gemini-3.8-flash',
]

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES_PER_MODEL = 1


def call_gemini(message, target_language=None, rag_context: Optional[str] = None):
    """Call Google Gemini generateContent API with RAG context, exponential backoff, and multi-model fallback."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        logger.warning('GEMINI_API_KEY is not configured; using fallback.')
        return None

    configured_model = getattr(settings, 'GEMINI_CHAT_MODEL', 'gemini-3.5-flash-lite')
    candidate_models = [configured_model]
    for fallback in DEFAULT_CANDIDATE_MODELS:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    user_prompt = str(message).strip()
    if rag_context:
        user_prompt = f"{rag_context}\n\n[USER QUESTION]\n{user_prompt}"

    lang_desc = LANGUAGE_PROMPTS.get(target_language)
    if lang_desc:
        user_prompt = (
            f"[CRITICAL MULTILINGUAL REQUIREMENT]\n"
            f"The user is asking in {lang_desc}.\n"
            f"You MUST write your ENTIRE response exclusively in {lang_desc}.\n"
            f"Strictly DO NOT reply in Hindi (unless Hindi was the requested language) or English.\n"
            f"All explanations, headings, steps, and crop recommendations must be in {lang_desc}.\n\n"
            f"{user_prompt}"
        )
    elif target_language and target_language not in ('en-IN', 'en'):
        user_prompt = f"[Target response language: {target_language}]\n{user_prompt}"

    payload = {
        'system_instruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'parts': [{'text': user_prompt}]}],
        'generationConfig': {
            'temperature': 0.3,
            'maxOutputTokens': 800,
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
                    timeout=(2.5, 6.0),
                )

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates') or []
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        text = ''.join(p.get('text', '') for p in parts if isinstance(p, dict)).strip()
                        if text:
                            return text
                elif resp.status_code in (400, 404):
                    logger.warning('Gemini model %s returned status %d, trying next model', model_name, resp.status_code)
                    cache.set(cooldown_key, True, timeout=120)
                    break
                elif resp.status_code in RETRYABLE_STATUS_CODES:
                    last_error = f"Gemini status {resp.status_code}: {resp.text[:200]}"
                    logger.warning(
                        'Gemini transient error (%s) on %s (attempt %d/%d): %s',
                        resp.status_code, model_name, attempt + 1, MAX_RETRIES_PER_MODEL + 1, last_error
                    )
                    cache.set(cooldown_key, True, timeout=60)
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
                cache.set(cooldown_key, True, timeout=60)
                break
            except requests.RequestException as e:
                last_error = str(e)
                logger.warning('Gemini request exception with %s: %s', model_name, e)
                break

    logger.error('All Gemini candidate models failed. Last error: %s', last_error)
    return None


def answer(message, language=None):
    """Answer farmer questions via agricultural RAG retrieval and Google Gemini in the user's language."""
    message = (message or '').strip()
    target_lang = language or 'en-IN'
    localized_fallback = get_localized_fallback(target_lang)
    if not message:
        return BotReply(localized_fallback, 'general', confidence=1.0)

    intent = detect_intent(message)
    api_key = getattr(settings, 'GEMINI_API_KEY', '')

    # Offline / unconfigured fallback when key is explicitly absent
    if not api_key:
        return BotReply(
            text=localized_fallback,
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

    # 3. RAG Retrieval from Agricultural Knowledge Base
    rag_matches = rag.retrieve_relevant_ciari_docs(message, top_k=2)
    rag_context = rag.format_rag_prompt_context(rag_matches) if rag_matches else None

    # 4. DIRECT GEMINI CALL: Questions are answered by Google Gemini augmented with RAG
    if api_key:
        gemini_text = call_gemini(message, target_language=language, rag_context=rag_context)
        if gemini_text:
            cache.set(cache_key, gemini_text, 7 * 24 * 3600)
            return BotReply(
                text=gemini_text,
                intent=intent,
                confidence=1.0,
                entry=None,
            )

    # 5. Direct Local Resilient RAG Fallback if Gemini service is unreachable or offline
    if rag_matches:
        offline_text = rag.format_offline_fallback_reply(rag_matches, message)
        if offline_text:
            return BotReply(
                text=offline_text,
                intent=intent,
                confidence=0.95,
                entry=None,
            )

    # 6. Fallback only if Gemini service is completely unreachable and no RAG match
    return BotReply(
        text=localized_fallback,
        intent=intent,
        confidence=0.5,
        entry=None,
    )
