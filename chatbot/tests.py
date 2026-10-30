import json
import re
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from . import engine, sarvam
from .models import ChatMessage


class EngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_knowledge', verbosity=0)

    def test_matches_scheme_question_with_source(self):
        reply = engine.answer('how much money does pm kisan give')
        self.assertIsNotNone(reply.entry)
        self.assertIn('6,000', reply.text)
        self.assertIn('PM-KISAN', reply.entry.source)

    def test_matches_pest_question(self):
        reply = engine.answer('armyworm attacking my maize crop what to spray')
        self.assertIn('emamectin', reply.text)

    def test_scheme_questions_get_scheme_answers(self):
        # Regression: "rice" used to outweigh "schemes" and return a fertilizer answer.
        cases = {
            'government schemes for rice growers': 'rice paddy farmers',
            'what are the government scheme provide for farmer': 'main government schemes',
            'what are the scheme provide for farmers recent news': 'main government schemes',
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                reply = engine.answer(query)
                self.assertIsNotNone(reply.entry)
                self.assertEqual(reply.entry.intent, 'scheme')
                self.assertIn(expected, reply.entry.question)

    def test_tolerates_misspellings(self):
        reply = engine.answer('how much and which fertizer i have to apply to get a best yeild')
        self.assertIsNotNone(reply.entry)
        self.assertEqual(reply.entry.intent, 'fertilizer')

    def test_greeting_and_weather_intents(self):
        self.assertEqual(engine.answer('namaste').intent, 'greeting')
        self.assertEqual(engine.answer('Greetings.').intent, 'greeting')  # how Sarvam translates ನಮಸ್ಕಾರ
        self.assertEqual(engine.answer('will it rain tomorrow?').intent, 'weather')
        self.assertEqual(engine.answer('what is the jowar price today').intent, 'market')
        self.assertIsNotNone(engine.answer('how to sell crop online').entry)

    def test_unknown_question_falls_back(self):
        reply = engine.answer('quantum chromodynamics lattice gauge')
        self.assertIsNone(reply.entry)
        self.assertIn('Kisan Call Centre', reply.text)


@override_settings(SARVAM_API_KEY='')
class ChatApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_knowledge', verbosity=0)

    def test_api_returns_reply_and_logs_message(self):
        resp = self.client.post(reverse('chatbot:api'), json.dumps({'message': 'fertilizer dose for wheat'}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('85 kg urea', data['reply'])
        self.assertTrue(data['source'])
        self.assertEqual(ChatMessage.objects.count(), 1)

    def test_api_rejects_empty_and_bad_json(self):
        url = reverse('chatbot:api')
        self.assertEqual(self.client.post(url, '{}', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(url, 'not json', content_type='application/json').status_code, 400)


KANNADA_Q = 'ಗೋಧಿಗೆ ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?'


def fake_translate(text, source, target, kind='answer'):
    if source == 'kn-IN' and target == 'en-IN':
        return 'How much fertilizer should be applied to wheat?'
    if source == 'en-IN' and target == 'kn-IN':
        return f'[kn] {text}'
    raise AssertionError(f'unexpected translation {source}->{target}')


@override_settings(SARVAM_API_KEY='test-key')
@patch.object(sarvam, 'translate', side_effect=fake_translate)
@patch.object(sarvam, 'detect_language')
class MultilingualTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_knowledge', verbosity=0)

    def post(self, message):
        return self.client.post(reverse('chatbot:api'), json.dumps({'message': message}),
                                content_type='application/json').json()

    def test_kannada_question_answered_in_kannada_from_knowledge_base(self, detect, translate):
        detect.return_value = 'kn-IN'
        data = self.post(KANNADA_Q)
        self.assertEqual(data['language'], 'kn-IN')
        self.assertTrue(data['reply'].startswith('[kn] '))
        self.assertIn('85 kg urea', data['reply'])  # wheat fertilizer entry, translated back
        self.assertIn('Wheat', data['source'])
        msg = ChatMessage.objects.get()
        self.assertEqual(msg.message, KANNADA_Q)
        self.assertEqual(msg.message_en, 'How much fertilizer should be applied to wheat?')
        self.assertEqual(msg.language, 'kn-IN')

    def test_english_question_skips_translation(self, detect, translate):
        detect.return_value = 'en-IN'
        data = self.post('fertilizer for wheat')
        self.assertEqual(data['language'], 'en-IN')
        translate.assert_not_called()

    def test_falls_back_to_english_when_sarvam_fails(self, detect, translate):
        detect.side_effect = sarvam.SarvamError('down')
        data = self.post('fertilizer for wheat')
        self.assertEqual(data['language'], 'en-IN')
        self.assertIn('85 kg urea', data['reply'])


@override_settings(SARVAM_API_KEY='test-key')
@patch.object(sarvam, 'translate', side_effect=fake_translate)
@patch.object(sarvam, 'transcribe')
class VoiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_knowledge', verbosity=0)

    def upload(self, size=1000):
        return {'audio': SimpleUploadedFile('question.webm', b'0' * size, content_type='audio/webm')}

    def test_voice_question_is_transcribed_and_answered_in_same_language(self, transcribe, translate):
        transcribe.return_value = (KANNADA_Q, 'kn-IN')
        data = self.client.post(reverse('chatbot:voice'), self.upload()).json()
        self.assertEqual(data['transcript'], KANNADA_Q)
        self.assertEqual(data['language'], 'kn-IN')
        self.assertIn('85 kg urea', data['reply'])
        self.assertTrue(ChatMessage.objects.get().is_voice)

    def test_voice_errors(self, transcribe, translate):
        url = reverse('chatbot:voice')
        self.assertEqual(self.client.post(url).status_code, 400)
        transcribe.return_value = ('', 'en-IN')
        self.assertEqual(self.client.post(url, self.upload()).status_code, 422)
        transcribe.side_effect = sarvam.SarvamError('down')
        self.assertEqual(self.client.post(url, self.upload()).status_code, 503)

    def test_dictation_returns_text_only_and_logs_nothing(self, transcribe, translate):
        transcribe.return_value = (KANNADA_Q, 'kn-IN')
        data = self.client.post(reverse('chatbot:transcribe'), self.upload()).json()
        self.assertEqual(data, {'transcript': KANNADA_Q, 'language': 'kn-IN'})
        self.assertFalse(ChatMessage.objects.exists())  # not a question until the farmer presses Send
        translate.assert_not_called()

    def test_mic_button_only_shown_when_key_configured(self, transcribe, translate):
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_user('f', password='pw'))
        self.assertContains(self.client.get(reverse('chatbot:chat')), 'data-mic')
        with override_settings(SARVAM_API_KEY=''):
            self.assertNotContains(self.client.get(reverse('chatbot:chat')), 'data-mic')


class TranslateChunkingTests(TestCase):
    def test_long_text_split_on_lines_under_limit(self):
        text = ('x' * 900 + '\n') * 5
        chunks = list(sarvam._chunks(text, 2000))
        self.assertEqual(''.join(chunks), text)
        self.assertTrue(all(len(c) <= 2000 for c in chunks))


class PlainLanguageTests(TestCase):
    """Farmers should see full names ('potash', 'grams per litre'), not chemistry shorthand."""
    SHORTHAND = re.compile(r'\bkg [NPK]\b|P2O5|K2O|\b[NPK] and [NPK]\b|\d ?g/L\b|\d ?ml/L\b|/litre|kg/ha')

    def test_knowledge_base_and_disease_advice_avoid_shorthand(self):
        from disease.treatments import TREATMENTS
        with open(settings.BASE_DIR / 'data' / 'knowledge_base.json', encoding='utf-8') as fh:
            texts = [e['answer'] for e in json.load(fh)] + list(TREATMENTS.values())
        offenders = [t[:80] for t in texts if self.SHORTHAND.search(t)]
        self.assertEqual(offenders, [])


@override_settings(SARVAM_API_KEY='test-key')
@patch.object(sarvam, 'speak_reply', return_value=['bXAz'])
class SpeakTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.owner = User.objects.create_user('owner', password='pw')
        self.other = User.objects.create_user('other', password='pw')
        self.msg = ChatMessage.objects.create(user=self.owner, message='q', response='ಉತ್ತರ',
                                              response_en='Answer', language='kn-IN')

    def test_owner_gets_female_voice_audio_in_reply_language(self, speak):
        self.client.force_login(self.owner)
        data = self.client.post(reverse('chatbot:speak', args=[self.msg.pk])).json()
        self.assertEqual(data, {'audios': ['bXAz'], 'format': 'mp3'})
        # Speech is built from the English reply (symbols cleaned) and then translated.
        speak.assert_called_once_with('Answer', 'kn-IN')

    def test_cannot_speak_someone_elses_reply(self, speak):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('chatbot:speak', args=[self.msg.pk])).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.post(reverse('chatbot:speak', args=[self.msg.pk])).status_code, 404)
        speak.assert_not_called()

    def test_chat_reply_includes_message_id_for_listening(self, speak):
        with patch.object(sarvam, 'detect_language', return_value='en-IN'):
            data = self.client.post(reverse('chatbot:api'), json.dumps({'message': 'hello'}),
                                    content_type='application/json').json()
        self.assertTrue(ChatMessage.objects.filter(pk=data['message_id']).exists())



class SpeechTextTests(TestCase):
    """Text-to-speech reads '/' as 'by' and '+' as 'plus'; speech must contain only words."""

    def test_symbols_become_words(self):
        cases = {
            '• PM-KISAN – Rs 6,000/year (pmkisan.gov.in)': 'PM-KISAN, 6,000 rupees per year',
            '53 kg DAP + 85 kg urea + 27 kg muriate of potash (MOP)': '53 kg DAP and 85 kg urea and 27 kg muriate of potash',
            'mancozeb 75% wettable powder (75 WP) at 2.5 grams': 'mancozeb 75% wettable powder at 2.5 grams',
            'alkaline/sodic soil; 2-4 weeks': 'alkaline or sodic soil; 2 to 4 weeks',
            'call 1800-180-1551 (6 am - 10 pm)': 'call 1800 180 1551 (6 am to 10 pm)',
        }
        for text, spoken in cases.items():
            with self.subTest(text=text):
                self.assertEqual(sarvam.speech_text(text), spoken)

    def test_knowledge_base_speech_has_no_spoken_symbols(self):
        with open(settings.BASE_DIR / 'data' / 'knowledge_base.json', encoding='utf-8') as fh:
            for entry in json.load(fh):
                spoken = sarvam.speech_text(entry['answer'])
                self.assertNotRegex(spoken, r'[/+•*]|\([A-Z]{2,}\)', entry['question'])

    @override_settings(SARVAM_API_KEY='test-key')
    @patch.object(sarvam, 'speak', return_value=['bXAz'])
    @patch.object(sarvam, 'translate', side_effect=lambda text, s, t: f'[{t}] {text}')
    def test_speak_reply_cleans_then_translates(self, translate, speak):
        sarvam.speak_reply('DAP + urea', 'hi-IN')
        speak.assert_called_once_with('[hi-IN] DAP and urea', 'hi-IN')


class GreetingTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user('nishchay', password='pw', first_name='nishchay')
        self.user.profile.preferred_language = 'kn'
        self.user.profile.save()
        self.url = reverse('chatbot:greeting')

    def test_greeting_by_time_of_day(self):
        from .views import greeting_text
        self.assertTrue(greeting_text('Asha', 8).startswith('Good morning, Asha!'))
        self.assertTrue(greeting_text('Asha', 14).startswith('Good afternoon, Asha!'))
        self.assertTrue(greeting_text('Asha', 19).startswith('Good evening, Asha!'))
        self.assertTrue(greeting_text('Asha', 2).startswith('Hello, Asha!'))
        self.assertIn("I'm Krishi Mitra", greeting_text('', 8))

    @override_settings(SARVAM_API_KEY='test-key')
    @patch.object(sarvam, 'speak', return_value=['bXAz'])
    @patch.object(sarvam, 'translate', side_effect=lambda text, s, t: f'[{t}] {text}')
    def test_greets_by_name_in_preferred_language(self, translate, speak):
        self.client.force_login(self.user)
        data = self.client.post(self.url, json.dumps({'hour': 9}), content_type='application/json').json()
        self.assertEqual(data['language'], 'kn-IN')
        self.assertTrue(data['text'].startswith('[kn-IN] Good morning, Nishchay!'))
        self.assertEqual(data['audios'], ['bXAz'])
        speak.assert_called_once_with(data['text'], 'kn-IN')

    @override_settings(SARVAM_API_KEY='test-key')
    @patch.object(sarvam, 'translate', side_effect=sarvam.SarvamError('down'))
    def test_falls_back_to_english_text_without_audio(self, translate):
        self.client.force_login(self.user)
        data = self.client.post(self.url, json.dumps({'hour': 20}), content_type='application/json').json()
        self.assertEqual(data['language'], 'en-IN')
        self.assertTrue(data['text'].startswith('Good evening, Nishchay!'))
        self.assertEqual(data['audios'], [])

    def test_rejects_missing_or_bad_hour(self):
        for body in ['{}', '{"hour": 25}', '{"hour": "x"}', 'nope']:
            with self.subTest(body=body):
                self.assertEqual(self.client.post(self.url, body, content_type='application/json').status_code, 400)
