"""Farmer Community Translation Engine.

Integrates with Sarvam AI for real-time multilingual translation across 22 Indian languages,
with robust agricultural fallback translations when offline or in sandboxed networks.
"""
import logging
from django.conf import settings
from chatbot import sarvam

logger = logging.getLogger(__name__)

# Common agricultural translations for instantaneous fallback
AGRI_GLOSSARY = {
    'hi': {
        'Help identifying problem with my Chilli': 'मेरी मिर्च की फसल में समस्या की पहचान करने में मदद करें',
        'Help identifying problem with my Tomato': 'मेरे टमाटर की फसल में समस्या की पहचान करने में मदद करें',
        'Plantix has detected a possible problem with my Capsicum & Chilli. I was given a few possibilities: ‼️ #Helicoverpa Caterpillar, ‼️ #Sunburn or ‼️ #Healthy. Can you help me identifying the issue?':
            'प्लेंटिक्स ने मेरी शिमला मिर्च और मिर्च में एक संभावित समस्या का पता लगाया है। मुझे कुछ संभावनाएं दी गई हैं: ‼️ #हेलिकोवर्पा इल्ली, ‼️ #धूप से झुलसना या ‼️ #स्वस्थ। क्या आप समस्या पहचानने में मेरी मदद कर सकते हैं?',
        'Plantix has detected a possible problem with my Tomato. I was given a few possibilities: ‼️ #Early Blight, ‼️ #Septoria or ‼️ #Healthy. Lower leaves are turning yellow with brown target-like concentric rings.':
            'प्लेंटिक्स ने मेरे टमाटर में एक समस्या का पता लगाया है। मुझे कुछ संभावनाएं दी गईं: ‼️ #अगेती झुलसा (अर्ली ब्लाइट), ‼️ #सेप्टोरिया या ‼️ #स्वस्थ। निचली पत्तियां भूरे गोल छल्लों के साथ पीली पड़ रही हैं।',
        'Powdery white patches spreading on pumpkin leaves': 'कद्दू की पत्तियों पर सफेद चूर्ण जैसे धब्बे तेजी से फैल रहे हैं',
        'Yellowing leaf tips in Paddy crop (30 DAT)': 'धान की फसल में पत्तियों के सिरे पीले पड़ रहे हैं (रोपाई के 30 दिन बाद)',
        'Yellow stripe-like rust spots appearing after rain': 'बारिश के बाद पत्तियों पर पीली धारियों जैसे रतुआ (रस्ट) के धब्बे दिख रहे हैं',
        'Fruit rot and baby zucchini drop in polytunnel': 'पॉलीटनेल में छोटे तोरी के फल सड़ रहे हैं और गिर रहे हैं',
        '#Helicoverpa Caterpillar': '#हेलिकोवर्पा इल्ली',
        '#Sunburn': '#धूप से झुलसना',
        '#Healthy': '#स्वस्थ',
        '#Early Blight': '#अगेती झुलसा',
        '#Septoria': '#सेप्टोरिया',
        '#Powdery Mildew': '#सफेद चूर्ण (पाउडरी मिल्ड्यू)',
        '#Organic Control': '#जैविक नियंत्रण',
        '#Paddy': '#धान',
        '#Bacterial Blight': '#जीवाणु झुलसा',
        '#Yellow Rust': '#पीला रतुआ',
        '#Pollination': '#परागण',
    },
    'mr': {
        'Help identifying problem with my Chilli': 'माझ्या मिरची पिकातील समस्या ओळखण्यासाठी मदत करा',
        'Help identifying problem with my Tomato': 'माझ्या टोमॅटो पिकातील समस्या ओळखण्यासाठी मदत करा',
        'Powdery white patches spreading on pumpkin leaves': 'भोपळ्याच्या पानांवर पांढरे डाग पसरत आहेत',
        'Yellowing leaf tips in Paddy crop (30 DAT)': 'भाताच्या पिकात पानांची टोके पिवळी पडत आहेत',
        '#Helicoverpa Caterpillar': '#शेंगा पोखरनारी अळी',
        '#Sunburn': '#उन्हाचा तडाखा',
        '#Early Blight': '#लवकर येणारा करपा',
        '#Powdery Mildew': '#भुरी रोग',
    },
    'kn': {
        'Help identifying problem with my Chilli': 'ನನ್ನ ಮೆಣಸಿನಕಾಯಿ ಬೆಳೆಯ ಸಮಸ್ಯೆಯನ್ನು ಗುರುತಿಸಲು ಸಹಾಯ ಮಾಡಿ',
        'Help identifying problem with my Tomato': 'ನನ್ನ ಟೊಮೇಟೊ ಬೆಳೆಯ ಸಮಸ್ಯೆಯನ್ನು ಗುರುತಿಸಲು ಸಹಾಯ ಮಾಡಿ',
        'Powdery white patches spreading on pumpkin leaves': 'ಕುಂಬಳಕಾಯಿ ಎಲೆಗಳ ಮೇಲೆ ಬಿಳಿ ಮಚ್ಚೆಗಳು ಹರಡುತ್ತಿವೆ',
        '#Helicoverpa Caterpillar': '#ಕಾಯಿಕೊರಕ ಹುಳು',
        '#Sunburn': '#ಬಿಸಿಲಿನ ಹಾನಿ',
    }
}


def translate_text(text: str, target_lang: str = 'hi') -> str:
    """Translate text to target language using Sarvam AI with offline agricultural fallback."""
    if not text or not text.strip():
        return text

    # Check exact glossary match
    lang_code = target_lang[:2].lower()
    if lang_code in AGRI_GLOSSARY and text.strip() in AGRI_GLOSSARY[lang_code]:
        return AGRI_GLOSSARY[lang_code][text.strip()]

    # Attempt Sarvam AI if configured
    if sarvam.is_configured():
        try:
            target_bcp47 = f"{lang_code}-IN" if lang_code != 'en' else 'en-IN'
            source_bcp47 = 'en-IN'
            res = sarvam.translate(text, source_bcp47, target_bcp47)
            if res and res.strip():
                return res
        except Exception as e:
            logger.info("Sarvam AI translation unavailable, applying fallback: %s", e)

    # Word-level fallback replacement if phrase wasn't found in glossary
    translated = text
    if lang_code in AGRI_GLOSSARY:
        for en_phrase, target_phrase in AGRI_GLOSSARY[lang_code].items():
            if en_phrase in translated:
                translated = translated.replace(en_phrase, target_phrase)

    return translated

