import json
import re
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .forms import RegisterForm
from .languages import LANGUAGE_CHOICES, available_languages, SARVAM_CODES, RTL_LANGUAGES
from crops.forms import YieldForm
from weather.services import advisories


BUNDLE = {'crops': ['Rice'], 'seasons': ['Kharif'], 'states': ['Karnataka'],
          'metrics': {'time_2016_2020': {'random_forest': {'r2': .83, 'rmse': 1.2}}},
          'latest_year': 2020}
HEADINGS = {'hi': 'डैशबोर्ड', 'kn': 'ಮುಖಪುಟ', 'te': 'డ్యాష్‌బోర్డ్',
            'ta': 'முகப்புப் பலகை', 'mr': 'मुख्य पान'}


@override_settings(SARVAM_API_KEY='', DATA_GOV_IN_API_KEY='')
class FarmerLanguageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('local-farmer', password='My-farm-secure!')
        self.client.force_login(self.user)

    def set_language(self, code):
        self.user.profile.preferred_language = code
        self.user.profile.save(update_fields=['preferred_language'])

    @patch('crops.views.load_bundle', return_value=BUNDLE)
    @patch('weather.views.fetch_forecast', return_value=[])
    @patch('market.views.get_states', return_value=[])
    @patch('market.views.fetch_prices', return_value=None)
    def test_saved_language_is_used_across_all_pages_and_overrides_browser(self, *_):
        for code, heading in HEADINGS.items():
            self.set_language(code)
            for path in ['/', '/accounts/dashboard/', '/accounts/profile/', '/crops/',
                         '/crops/yield/', '/disease/', '/weather/', '/market/', '/chat/']:
                with self.subTest(code=code, path=path):
                    response = self.client.get(path, HTTP_ACCEPT_LANGUAGE='en')
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response['Content-Language'], code)
                    self.assertContains(response, f'<html lang="{code}"')
                    self.assertContains(response, heading)
                    self.assertNotContains(response, '>Crop Advisor<')
            catalog = self.client.get('/jsi18n/').content.decode()
            self.assertIn('Thinking', catalog)
            self.assertNotIn('"Thinking…": "Thinking…"', catalog)

    def test_signup_applies_preference_and_success_message_immediately(self):
        self.client.logout()
        response = self.client.post(reverse('accounts:register'), {
            'email': 'new-farmer@example.com', 'state': 'Karnataka', 'district': 'Mandya', 'password1': 'My-farm-secure!',
            'password2': 'My-farm-secure!', 'preferred_language': 'kn',
        }, follow=True)
        self.assertEqual(response['Content-Language'], 'kn')
        self.assertContains(response, 'ನಿಮ್ಮ ರೈತ ಖಾತೆ ಸಿದ್ಧವಾಗಿದೆ')
        self.assertContains(response, 'ಮುಖಪುಟ')

    def test_profile_change_applies_to_next_page_and_persists_after_login(self):
        response = self.client.post('/accounts/profile/', {'preferred_language': 'ta'}, follow=True)
        self.assertContains(response, 'சுயவிவரம் புதுப்பிக்கப்பட்டது')
        self.assertEqual(response['Content-Language'], 'ta')
        self.client.logout()
        self.client.login(username='local-farmer', password='My-farm-secure!')
        self.assertEqual(self.client.get('/accounts/dashboard/')['Content-Language'], 'ta')

    def test_invalid_saved_language_falls_back_and_does_not_leak_between_users(self):
        self.set_language('xx')
        self.assertEqual(self.client.get('/')['Content-Language'], 'en')
        self.set_language('kn')
        self.assertEqual(self.client.get('/')['Content-Language'], 'kn')
        english = User.objects.create_user('english-farmer')
        self.client.force_login(english)
        self.assertEqual(self.client.get('/')['Content-Language'], 'en')
        self.assertEqual(translation.get_language(), settings.LANGUAGE_CODE)

    def test_invalid_form_uses_native_labels_and_validation(self):
        self.set_language('kn')
        response = self.client.post('/crops/', {'N': 'not-a-number'})
        self.assertContains(response, 'ಸಾರಜನಕ')
        self.assertContains(response, 'ಸಂಖ್ಯೆ ನಮೂದಿಸಿ')
        self.assertContains(response, 'ಈ ಮಾಹಿತಿ ಅಗತ್ಯ')

    @patch('chatbot.sarvam.translate', return_value='ನಿಮ್ಮ ಬೆಳೆ ಸಲಹೆ')
    @patch('chatbot.sarvam.detect_language', return_value='en-IN')
    @patch('chatbot.sarvam.is_configured', return_value=True)
    def test_english_question_can_receive_reply_in_saved_native_language(self, configured, detect, translate):
        self.set_language('kn')
        response = self.client.post('/chat/api/', json.dumps({'message': 'Hello'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['language'], 'kn-IN')
        self.assertEqual(response.json()['reply'], 'ನಿಮ್ಮ ಬೆಳೆ ಸಲಹೆ')
        self.assertFalse(response.json()['translation_unavailable'])

    def test_chat_reports_translation_outage_without_claiming_english_is_native(self):
        self.set_language('kn')
        response = self.client.post('/chat/api/', json.dumps({'message': 'Hello'}), content_type='application/json')
        self.assertTrue(response.json()['translation_unavailable'])


class TranslationCatalogTests(SimpleTestCase):
    def test_every_literal_template_and_client_message_has_five_translations(self):
        rows = json.loads((settings.BASE_DIR / 'locale/ui/en.json').read_text())
        pattern = re.compile(r'''{% translate\s+("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*%}''')
        import ast
        for path in (settings.BASE_DIR / 'templates').rglob('*.html'):
            for match in pattern.finditer(path.read_text()):
                key = ast.literal_eval(match.group(1))
                self.assertIn(key, rows, f'{path}: {key}')
        for code, _ in available_languages():
            if code == 'en':
                continue
            with translation.override(code):
                for source in rows:
                    if source not in {', RMSE', 'm/s ·'}:
                        self.assertNotEqual(translation.gettext(source), source, f'{code}: {source}')
                form = RegisterForm()
                self.assertNotIn('Use at least', str(form['password1'].help_text))
                yield_form = YieldForm(bundle=BUNDLE)
                self.assertEqual(yield_form.fields['crop'].choices[1][0], 'Rice')
                self.assertNotEqual(yield_form.fields['crop'].choices[1][1], 'Rice')
                days = [{'rain_mm': 10, 'temp_max': 40, 'temp_min': 20,
                         'humidity': 90, 'wind_speed': 9}] * 3
                text = ' '.join(t for _, t in advisories(days, 10))
                self.assertNotIn('Heavy rain', text)
                self.assertIn('30', text)
                self.assertIn('10', text)

    def test_dynamic_treatment_sources_are_in_the_translation_inventory(self):
        from disease.treatments import TREATMENTS, GENERAL_HYGIENE, HEALTHY_ADVICE
        source = json.loads((settings.BASE_DIR / 'locale/ui/en.json').read_text())
        for text in [*TREATMENTS.values(), GENERAL_HYGIENE, HEALTHY_ADVICE]:
            self.assertIn(text, source)
            for code, _ in available_languages():
                if code == 'en':
                    continue
                with translation.override(code):
                    self.assertNotEqual(translation.gettext(text), text, f'{code}: untranslated treatment')

    def test_disease_result_text_is_bundled_in_every_available_language(self):
        from accounts.localization import ui_text
        from disease.treatments import advice_for
        classes = json.loads((settings.BASE_DIR / 'ml/models/disease_classes.json').read_text())
        for code, _ in available_languages():
            if code == 'en':
                continue
            with translation.override(code):
                for name in classes:
                    result = advice_for(name)
                    for key in ('plant', 'disease', 'treatment'):
                        self.assertNotEqual(ui_text(result[key]), result[key], f'{code}: {name}: {key}')

    def test_nationwide_registry_and_unfinished_catalogs(self):
        self.assertEqual(len(LANGUAGE_CHOICES), 23)
        self.assertEqual(SARVAM_CODES['or'], 'od-IN')
        self.assertEqual(RTL_LANGUAGES, {'ks', 'sd', 'ur'})
        for code, _ in available_languages():
            self.assertIn(code, dict(LANGUAGE_CHOICES))
        for code, _ in available_languages():
            self.assertTrue((settings.BASE_DIR / 'locale/ui' / f'{code}.json').exists())


class CatalogGenerationTests(SimpleTestCase):
    def test_translation_preserves_runtime_placeholders(self):
        from scripts.translate_ui_offline import protect, validate
        text, tokens = protect('Rain %(rain)s mm')
        self.assertEqual(text, 'Rain 8675309001 mm')
        self.assertEqual(validate('Rain %(rain)s mm', 'ಮಳೆ 8675309001 ಮಿಮೀ', tokens), 'ಮಳೆ %(rain)s ಮಿಮೀ')

    def test_translation_rejects_missing_placeholders(self):
        from scripts.translate_ui_offline import protect, validate
        _, tokens = protect('Rain %(rain)s mm')
        with self.assertRaises(ValueError):
            validate('Rain %(rain)s mm', 'ಮಳೆ TOKEN ಮಿಮೀ', tokens)

    def test_translation_rejects_changed_numbers(self):
        from scripts.translate_ui_offline import validate
        with self.assertRaises(ValueError):
            validate('5 mm', '9 ಮಿಮೀ', {})

    def test_translation_rejects_repetition(self):
        from scripts.translate_ui_offline import validate
        with self.assertRaises(ValueError):
            validate('Weather', 'ಮಳೆ ' * 20, {})

    @patch('socket.socket', side_effect=AssertionError('Network access forbidden'))
    def test_catalog_status_uses_no_network_or_credits(self, socket):
        from django.core.management import call_command
        from io import StringIO
        output = StringIO()
        call_command('translate_ui', '--status', stdout=output)
        self.assertIn('kn:', output.getvalue())

    def test_offline_generator_covers_exactly_the_scheduled_language_registry(self):
        from scripts.translate_ui_offline import LANGUAGES
        from accounts.languages import LANGUAGE_CODES
        self.assertEqual(set(LANGUAGES), LANGUAGE_CODES - {'en'})

    def test_native_numerals_preserve_numeric_values(self):
        from scripts.translate_ui_offline import validate
        self.assertEqual(validate('5 mm', '৫ মিমি', {}), '5 মিমি')

    def test_medical_protocol_protection_preserves_formulation_and_per_litre_dose(self):
        from scripts.translate_ui_offline import protect, validate
        from disease.treatments import TREATMENTS
        source = TREATMENTS['powdery mildew']
        _, tokens = protect(source, strict=True)
        self.assertEqual(list(tokens.values()), ['sulphur 80 WP: 2-3 g/L', 'hexaconazole 5 EC: 1 mL/L'])
        output = 'छिड़कें ' + ' या '.join(tokens)
        restored = validate(source, output, tokens)
        self.assertIn('2-3 g/L', restored)
        self.assertIn('1 mL/L', restored)

    def test_percent_escaping_remains_safe_when_rechecking_saved_translations(self):
        from scripts.translate_ui_offline import protect, validate
        source = 'Moisture %(n)s%%'
        _, tokens = protect(source)
        translated = validate(source, 'नमी 8675309001%', tokens)
        self.assertEqual(translated, 'नमी %(n)s%%')
        self.assertEqual(validate(source, translated, {}), translated)

    def test_invalid_unicode_output_is_rejected(self):
        from scripts.translate_ui_offline import validate
        with self.assertRaises(ValueError):
            validate('Hello', 'ꯃ\ufffd', {})

class RegisterLanguageAvailabilityTests(SimpleTestCase):
    def test_register_only_offers_complete_compiled_languages(self):
        from tempfile import TemporaryDirectory
        from accounts import languages
        with TemporaryDirectory() as folder:
            root = Path(folder)
            ui = root / 'ui'
            ui.mkdir()
            for code, messages in {'en': {'A': 'A', 'B': 'B'},
                                   'hi': {'A': 'क', 'B': 'ख'},
                                   'kn': {'A': 'ಕ'},
                                   'te': {'A': 'అ', 'B': 'ఆ'}}.items():
                (ui / f'{code}.json').write_text(json.dumps(messages))
            for code in ('hi', 'kn'):
                compiled = root / code / 'LC_MESSAGES'
                compiled.mkdir(parents=True)
                (compiled / 'django.mo').write_bytes(b'present')
            languages.available_languages.cache_clear()
            try:
                with patch.object(languages, 'UI_FOLDER', ui):
                    choices = dict(RegisterForm().fields['preferred_language'].choices)
                    self.assertEqual(set(choices), {'en', 'hi'})
            finally:
                languages.available_languages.cache_clear()
