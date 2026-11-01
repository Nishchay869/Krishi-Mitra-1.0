import json
import re
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from . import engine, sarvam
from .models import ChatMessage


def mock_gemini_post(*args, **kwargs):
    """Mock Gemini API requests.post for unit tests without network access."""
    json_payload = kwargs.get('json', {})
    contents = json_payload.get('contents', [])
    prompt_text = ''
    if contents and 'parts' in contents[0]:
        prompt_text = contents[0]['parts'][0].get('text', '')

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    if any(k in prompt_text.lower() for k in ['sort a list', 'python', 'cricket', 'prime minister']):
        reply_text = (
            "I am Krishi Mitra's Farm Assistant. I am designed exclusively to assist with agriculture, "
            "crops, farming practices, weather, mandi prices, fertilizers, and Krishi Mitra platform services. "
            "I cannot answer queries outside the agricultural domain. Please ask an agriculture-related question."
        )
    elif 'ಯಾವ ಗೊಬ್ಬರ' in prompt_text or 'ಗೋಧಿ' in prompt_text:
        reply_text = (
            "ಗೋಧಿ ಬೆಳೆಗೆ ಎಕರೆಗೆ 50 ಕೆಜಿ ಡಿಎಪಿ (DAP), 25 ಕೆಜಿ ಪೊಟ್ಯಾಷ್ (MOP) ಮತ್ತು 85 kg urea ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ."
        )
    elif 'pm kisan' in prompt_text.lower():
        reply_text = (
            "Under PM-KISAN (Pradhan Mantri Kisan Samman Nidhi), eligible farmers receive Rs 6,000 per year "
            "in three equal installments of Rs 2,000 directly into their bank accounts."
        )
    elif 'armyworm' in prompt_text.lower():
        reply_text = (
            "For controlling Fall Armyworm in maize, spray Emamectin Benzoate 5% SG at 0.4 g/liter of water "
            "or Chlorantraniliprole 18.5% SC at 0.3 ml/liter targeting the plant whorls."
        )
    elif 'fertilizer' in prompt_text.lower() or 'wheat' in prompt_text.lower():
        reply_text = (
            "For wheat, the standard balanced fertilizer dose per acre is 50 kg DAP, 85 kg urea, and 25 kg MOP."
        )
    else:
        reply_text = "Krishi Mitra Farm Assistant is here to assist with your agricultural and crop advisory questions."

    mock_resp.json.return_value = {
        'candidates': [
            {'content': {'parts': [{'text': reply_text}]}}
        ]
    }
    return mock_resp


@override_settings(GEMINI_API_KEY='test-gemini-key')
class EngineTests(TestCase):
    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_gemini_answers_farming_question_without_chunks(self, mock_post):
        reply = engine.answer('how much money does pm kisan give')
        self.assertIsNone(reply.entry)  # Chunks removed!
        self.assertIn('6,000', reply.text)
        data = reply.as_dict()
        self.assertIsNone(data['source'])  # No source chunk
        self.assertIsNone(data['source_url'])

    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_gemini_answers_pest_question(self, mock_post):
        reply = engine.answer('armyworm attacking my maize crop what to spray')
        self.assertIsNone(reply.entry)
        self.assertIn('Emamectin', reply.text)

    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_gemini_boundary_guardrail_refusal(self, mock_post):
        reply = engine.answer('write a python script to sort a list of numbers')
        self.assertIn('Krishi Mitra', reply.text)
        self.assertIn('cannot answer queries outside the agricultural domain', reply.text)

    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_gemini_answers_in_user_language_kannada(self, mock_post):
        reply = engine.answer('ಗೋಧಿಗೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?')
        self.assertIn('ಗೋಧಿ', reply.text)
        self.assertIn('ಡಿಎಪಿ', reply.text)

    @override_settings(GEMINI_API_KEY='')
    def test_fallback_when_gemini_key_missing(self):
        reply = engine.answer('what fertilizer for wheat?')
        self.assertIn('Kisan Call Centre', reply.text)
        self.assertIsNone(reply.entry)


@override_settings(GEMINI_API_KEY='test-gemini-key', SARVAM_API_KEY='')
class ChatApiTests(TestCase):
    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_api_returns_reply_and_logs_message(self, mock_post):
        resp = self.client.post(
            reverse('chatbot:api'),
            json.dumps({'message': 'fertilizer dose for wheat'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('85 kg urea', data['reply'])
        self.assertIsNone(data['source'])  # Chunks removed!
        self.assertEqual(ChatMessage.objects.count(), 1)
        msg = ChatMessage.objects.first()
        self.assertIsNone(msg.matched_entry)  # No matched entry chunk

    def test_api_rejects_empty_and_bad_json(self):
        url = reverse('chatbot:api')
        self.assertEqual(self.client.post(url, '{}', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(url, 'not json', content_type='application/json').status_code, 400)


KANNADA_Q = 'ಗೋಧಿಗೆ ಎಷ್ಟು ಗೊಬ್ಬರ ಹಾಕಬೇಕು?'


@override_settings(GEMINI_API_KEY='test-gemini-key', SARVAM_API_KEY='test-key')
class MultilingualTests(TestCase):
    def post(self, message):
        return self.client.post(reverse('chatbot:api'), json.dumps({'message': message}),
                                content_type='application/json').json()

    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_kannada_question_answered_in_kannada_directly(self, mock_post):
        data = self.post(KANNADA_Q)
        self.assertEqual(data['language'], 'kn-IN')
        self.assertIn('ಗೋಧಿ', data['reply'])
        self.assertIsNone(data.get('source'))
        msg = ChatMessage.objects.first()
        self.assertEqual(msg.message, KANNADA_Q)
        self.assertEqual(msg.language, 'kn-IN')
        self.assertIsNone(msg.matched_entry)


@override_settings(GEMINI_API_KEY='test-gemini-key', SARVAM_API_KEY='test-key')
@patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
@patch.object(sarvam, 'transcribe')
class VoiceTests(TestCase):
    def upload(self, size=1000):
        return {'audio': SimpleUploadedFile('question.webm', b'0' * size, content_type='audio/webm')}

    def test_voice_question_is_transcribed_and_answered(self, transcribe, mock_post):
        transcribe.return_value = (KANNADA_Q, 'kn-IN')
        data = self.client.post(reverse('chatbot:voice'), self.upload()).json()
        self.assertEqual(data['transcript'], KANNADA_Q)
        self.assertEqual(data['language'], 'kn-IN')
        self.assertIn('ಗೋಧಿ', data['reply'])
        self.assertTrue(ChatMessage.objects.get().is_voice)
        self.assertIsNone(data.get('source'))

    def test_voice_errors(self, transcribe, mock_post):
        url = reverse('chatbot:voice')
        self.assertEqual(self.client.post(url).status_code, 400)
        transcribe.return_value = ('', 'en-IN')
        self.assertEqual(self.client.post(url, self.upload()).status_code, 422)
        transcribe.side_effect = sarvam.SarvamError('down')
        self.assertEqual(self.client.post(url, self.upload()).status_code, 503)

    def test_dictation_returns_text_only_and_logs_nothing(self, transcribe, mock_post):
        transcribe.return_value = (KANNADA_Q, 'kn-IN')
        data = self.client.post(reverse('chatbot:transcribe'), self.upload()).json()
        self.assertEqual(data, {'transcript': KANNADA_Q, 'language': 'kn-IN'})
        self.assertFalse(ChatMessage.objects.exists())

    def test_mic_button_only_shown_when_key_configured(self, transcribe, mock_post):
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


@override_settings(SARVAM_API_KEY='test-key', GEMINI_API_KEY='test-gemini-key')
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
        speak.assert_called_once_with('Answer', 'kn-IN')

    def test_cannot_speak_someone_elses_reply(self, speak):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('chatbot:speak', args=[self.msg.pk])).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.post(reverse('chatbot:speak', args=[self.msg.pk])).status_code, 404)
        speak.assert_not_called()

    @patch('chatbot.engine.requests.post', side_effect=mock_gemini_post)
    def test_chat_reply_includes_message_id_for_listening(self, mock_post, speak):
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
