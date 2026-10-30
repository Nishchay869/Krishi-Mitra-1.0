"""Nationwide language registry; only complete bundled UI catalogs are selectable."""
import json
from functools import lru_cache
from pathlib import Path

LANGUAGE_CHOICES = [
    ('en', 'English'), ('as', 'অসমীয়া'), ('bn', 'বাংলা'), ('brx', 'बड़ो'),
    ('doi', 'डोगरी'), ('gu', 'ગુજરાતી'), ('hi', 'हिन्दी'), ('kn', 'ಕನ್ನಡ'),
    ('ks', 'کٲشُر'), ('kok', 'कोंकणी'), ('mai', 'मैथिली'), ('ml', 'മലയാളം'),
    ('mni', 'মৈতৈলোন্'), ('mr', 'मराठी'), ('ne', 'नेपाली'), ('or', 'ଓଡ଼ିଆ'),
    ('pa', 'ਪੰਜਾਬੀ'), ('sa', 'संस्कृतम्'), ('sat', 'ᱥᱟᱱᱛᱟᱲᱤ'),
    ('sd', 'سنڌي'), ('ta', 'தமிழ்'), ('te', 'తెలుగు'), ('ur', 'اردو'),
]
LANGUAGE_CODES = {code for code, _ in LANGUAGE_CHOICES}
# Django/ISO uses 'or' for Odia; the Sarvam API uses 'od-IN'.
SARVAM_CODES = {code: f'{code}-IN' for code in LANGUAGE_CODES}
SARVAM_CODES['or'] = 'od-IN'
RTL_LANGUAGES = {'ks', 'sd', 'ur'}
UI_FOLDER = Path(__file__).resolve().parent.parent / 'locale' / 'ui'


@lru_cache(maxsize=1)
def available_languages():
    """Do not offer a language whose pages would silently fall back to English."""
    source = json.loads((UI_FOLDER / 'en.json').read_text())
    choices = []
    for code, label in LANGUAGE_CHOICES:
        path = UI_FOLDER / f'{code}.json'
        compiled = UI_FOLDER.parent / code / 'LC_MESSAGES' / 'django.mo'
        if code == 'en':
            choices.append((code, label))
        elif path.exists() and compiled.exists():
            messages = json.loads(path.read_text())
            if source.keys() <= messages.keys() and all(messages.get(key) for key in source):
                choices.append((code, label))
    return choices
