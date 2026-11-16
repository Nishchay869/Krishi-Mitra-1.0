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
    elif 'rain' in prompt_text.lower() and 'paddy' in prompt_text.lower():
        reply_text = (
            "Paddy requires 1,000 to 1,500 mm of rainfall throughout its growing season. "
            "Maintain 2–3 cm standing water at transplanting and 3–5 cm during flowering."
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
    def test_paddy_rainfall_returns_water_management_not_fertilizer(self, mock_post):
        reply = engine.answer('how much rain require for paddy growing')
        self.assertIn('1,000 to 1,500 mm', reply.text)
        self.assertNotIn('120 kg nitrogen', reply.text)
        self.assertIn(reply.intent, ('weather', 'irrigation'))

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
    @patch.object(sarvam, 'translate', side_effect=lambda text, s, t, kind='answer': f'[{t}] {text}')
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
    @patch.object(sarvam, 'translate', side_effect=lambda text, s, t, kind='answer': f'[{t}] {text}')
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


class ClearChatTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user('testfarmer', password='password123')
        self.clear_url = reverse('chatbot:clear')
        self.chat_page_url = reverse('chatbot:chat')

    def test_clear_chat_removes_messages_permanently(self):
        self.client.force_login(self.user)
        # Create chat messages
        ChatMessage.objects.create(user=self.user, message='hello', response='Hi farmer!')
        ChatMessage.objects.create(user=self.user, message='fertilizer for rice', response='Use urea.')
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 2)

        # Clear via api_clear
        resp = self.client.post(self.clear_url, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'cleared')
        self.assertEqual(resp.json()['count'], 2)
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 0)

        # Visiting chat_page afterwards returns empty history
        page_resp = self.client.get(self.chat_page_url)
        self.assertEqual(page_resp.status_code, 200)
        self.assertEqual(page_resp.context['history'], [])
        self.assertEqual(page_resp.context['history_json'], '[]')

    def test_navigating_to_chat_page_automatically_clears_prior_messages(self):
        self.client.force_login(self.user)
        # Farmer had older chat messages
        ChatMessage.objects.create(user=self.user, message='older question', response='older answer')
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 1)

        # Navigating to chat_page (e.g. from another section of the website) clears all older messages
        page_resp = self.client.get(self.chat_page_url)
        self.assertEqual(page_resp.status_code, 200)
        self.assertEqual(page_resp.context['history'], [])
        self.assertEqual(page_resp.context['history_json'], '[]')
        self.assertEqual(ChatMessage.objects.filter(user=self.user).count(), 0)


@override_settings(GEMINI_API_KEY='test-gemini-key')
class GeminiResilienceTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    @patch('chatbot.engine.time.sleep', return_value=None)
    @patch('chatbot.engine.requests.post')
    def test_gemini_503_failover_to_fallback_model(self, mock_post, mock_sleep):
        """When primary model experiences 503 high demand, failover to secondary model succeeds."""
        # 1st attempt: 503 UNAVAILABLE
        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_503.text = json.dumps({
            "error": {
                "code": 503,
                "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary.",
                "status": "UNAVAILABLE"
            }
        })

        # 2nd attempt: 200 OK from fallback model
        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Apply 50 kg DAP and 85 kg urea per acre.'}]}}]
        }

        mock_post.side_effect = [resp_503, resp_200]

        reply = engine.answer('sugarcane nutrient management')
        self.assertIn('Apply 50 kg DAP', reply.text)
        self.assertEqual(reply.confidence, 1.0)

    @patch('chatbot.engine.time.sleep', return_value=None)
    @patch('chatbot.engine.requests.post')
    def test_all_models_503_graceful_fallback(self, mock_post, mock_sleep):
        """When all Gemini models fail with 503, gracefully return fallback advisory without knowledge base."""
        resp_503 = MagicMock()
        resp_503.status_code = 503
        resp_503.text = '{"error": {"code": 503, "status": "UNAVAILABLE"}}'
        mock_post.return_value = resp_503

        reply = engine.answer('What is the recommended fertilizer for sugarcane?')
        self.assertIn('Kisan Call Centre', reply.text)
        self.assertIsNone(reply.entry)


class CIARIRAGTests(TestCase):
    """Unit tests for ICAR-CIARI RAG Knowledge Base and Prompt Augmentation."""

    def test_ciari_rag_retrieves_organic_tomato_package(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('how to control fruit borer in tomato organically', top_k=2)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertEqual(top['crop'], 'Tomato')
        self.assertIn('Fruit Borer', top['answer'])
        self.assertIn('Neem Oil', top['answer'])

    def test_ciari_rag_retrieves_coconut_package(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('what is the spacing and pit size for coconut in andaman', top_k=2)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertEqual(top['crop'], 'Coconut')
        self.assertIn('7.5 m x 7.5 m', top['answer'])
        self.assertIn('1 m x 1 m x 1 m', top['answer'])

    def test_ciari_rag_retrieves_broad_dhaniya_intercrop(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('how to cultivate broad dhaniya in coconut garden', top_k=2)
        self.assertTrue(len(matches) > 0)
        titles = [m.entry['title'] for m in matches]
        self.assertTrue(any('Broad Dhaniya' in t or 'Coconut' in t for t in titles))

    def test_ciari_rag_retrieves_arecanut_koleroga(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('how to control koleroga disease in arecanut', top_k=2)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertEqual(top['crop'], 'Arecanut')
        self.assertIn('Koleroga', top['title'])
        self.assertIn('Bordeaux mixture', top['answer'])

    def test_ciari_rag_retrieves_elephant_foot_yam(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('how to prepare elephant foot yam corm setts for planting', top_k=2)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertEqual(top['crop'], 'Elephant Foot Yam')
        self.assertIn('Gajendra', top['answer'])
        self.assertIn('cow dung slurry', top['answer'])

    def test_ciari_rag_prompt_augmentation(self):
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('how to control fruit borer in tomato organically', top_k=1)
        prompt_context = rag.format_rag_prompt_context(matches)
        self.assertIn('ICAR-CIARI', prompt_context)
        self.assertIn('Tomato', prompt_context)
        self.assertIn('CRITICAL INSTRUCTIONS FOR RESPONSE GENERATION', prompt_context)

    @override_settings(GEMINI_API_KEY='test-key')
    @patch('chatbot.engine.requests.post')
    def test_engine_passes_ciari_rag_context_to_gemini(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Based on ICAR-CIARI recommendations, spray Neem oil 5 ml/L for fruit borer in tomato.'}]}}]
        }
        mock_post.return_value = mock_resp

        reply = engine.answer('how to control fruit borer in tomato organically')
        self.assertIn('ICAR-CIARI', reply.text)
        self.assertIn('Neem oil', reply.text)

        # Verify that prompt payload sent to Gemini contains the CIARI context
        call_kwargs = mock_post.call_args[1]
        json_body = call_kwargs['json']
        user_content = json_body['contents'][0]['parts'][0]['text']
        self.assertIn('AUTHORITATIVE AGRICULTURAL REFERENCE (ICAR-CIARI PACKAGE OF PRACTICES)', user_content)
        self.assertIn('Tomato', user_content)

    def test_seed_knowledge_populates_ciari_database(self):
        from chatbot.models import KnowledgeEntry
        initial_count = KnowledgeEntry.objects.count()
        call_command('seed_knowledge')
        self.assertGreaterEqual(KnowledgeEntry.objects.count(), 50)
        self.assertTrue(KnowledgeEntry.objects.filter(source__icontains='ICAR-CIARI').exists())


class ExtendedAgriculturalRAGTests(TestCase):
    """Tests for multi-document RAG retrieval across CPG 2012, Horticulture, UAS Dharwad & Farmer Book."""

    def test_ragi_fertilizer_retrieval_and_cross_crop_isolation(self):
        """Querying Ragi fertilizer must retrieve Finger Millet (Ragi) and never Wheat, Cotton, or Tomato."""
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('What is the fertilizer dose for Ragi?', top_k=3)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertIn('Ragi', top['crop'])
        self.assertEqual(top['topic'], 'fertilizer_management')
        self.assertIn('60 kg N', top['answer'])
        # Verify no other crops in top matches
        for m in matches:
            self.assertIn('Ragi', m.entry['crop'])

    def test_cotton_pest_management_retrieval(self):
        """Querying cotton pests returns Cotton plant protection."""
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('How to manage bollworm and sucking pests in cotton?', top_k=2)
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0].entry['crop'], 'Cotton')
        self.assertIn('Cotton', matches[0].entry['title'])

    def test_uas_dharwad_natural_farming_retrieval(self):
        """Natural farming biostimulant query returns UAS Dharwad Jeevamrit advisory."""
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('How to prepare Jeevamrit and Beejamrit for natural farming in Karnataka?', top_k=2)
        self.assertTrue(len(matches) > 0)
        titles = [m.entry['title'] for m in matches]
        self.assertTrue(any('Jeevamrit' in t for t in titles))
        top = matches[0].entry
        self.assertIn('Jeevamrit', top['answer'])

    def test_farmerbook_soil_plant_nutrition_retrieval(self):
        """Deficiency query returns Farmer Book soil plant nutrition guide."""
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('What are nitrogen and phosphorus deficiency symptoms in crops?', top_k=2)
        self.assertTrue(len(matches) > 0)
        top = matches[0].entry
        self.assertTrue('deficiency' in top['answer'].lower() or 'nitrogen' in top['answer'].lower())

    def test_horticulture_mango_fertilizer_table(self):
        """Mango query retrieves Horticulture guide with table data."""
        from chatbot import rag
        matches = rag.retrieve_relevant_ciari_docs('What is the fertilizer schedule for Mango trees?', top_k=2)
        self.assertTrue(len(matches) > 0)
        self.assertEqual(matches[0].entry['crop'], 'Mango')
        self.assertTrue('|' in matches[0].entry['answer'] or 'FYM' in matches[0].entry['answer'])







def _sse_response(chunks, status=200):
    """Fake Gemini streamGenerateContent (alt=sse) response."""
    resp = MagicMock(status_code=status, text='')
    resp.iter_lines.return_value = [
        'data: ' + json.dumps({'candidates': [{'content': {'parts': [{'text': c}]}}]}) for c in chunks
    ]
    return resp


@override_settings(GEMINI_API_KEY='test-placeholder', SARVAM_API_KEY='')
class StreamingChatTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def _events(self, message):
        response = self.client.post(reverse('chatbot:api_stream'), json.dumps({'message': message}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.streaming)
        self.assertEqual(response['Content-Type'], 'application/x-ndjson; charset=utf-8')
        return [json.loads(line) for line in b''.join(response.streaming_content).decode().splitlines() if line]

    @patch('chatbot.engine.requests.post')
    def test_reply_arrives_piece_by_piece_and_is_saved(self, post):
        post.return_value = _sse_response(['Apply ', 'neem oil ', 'every 7 days.'])
        events = self._events('How do I control aphids on my chilli crop?')
        deltas = [e['text'] for e in events if e['type'] == 'delta']
        self.assertEqual(deltas, ['Apply ', 'neem oil ', 'every 7 days.'])
        done = events[-1]
        self.assertEqual(done['type'], 'done')
        self.assertEqual(done['reply'], 'Apply neem oil every 7 days.')
        self.assertFalse(any(e['type'] == 'replace' for e in events))
        self.assertEqual(ChatMessage.objects.get(pk=done['message_id']).response, 'Apply neem oil every 7 days.')
        self.assertEqual(post.call_args.kwargs['params']['alt'], 'sse')
        self.assertTrue(post.call_args.kwargs['stream'])

    @patch('chatbot.engine.requests.post')
    def test_greeting_is_sent_in_one_piece_without_calling_gemini(self, post):
        events = self._events('Hello')
        self.assertEqual(len([e for e in events if e['type'] == 'delta']), 1)
        self.assertEqual(events[-1]['type'], 'done')
        post.assert_not_called()

    @patch('chatbot.engine.requests.post')
    def test_gemini_failure_falls_back_to_a_reply(self, post):
        post.return_value = _sse_response([], status=503)
        events = self._events('How do I control aphids on my chilli crop?')
        self.assertEqual(events[-1]['type'], 'done')
        self.assertTrue(events[-1]['reply'])

    @patch('chatbot.sarvam.translate', return_value='ನೀಮ್ ಎಣ್ಣೆ ಬಳಸಿ')
    @patch('chatbot.sarvam.is_configured', return_value=True)
    @patch('chatbot.engine.requests.post')
    def test_translated_reply_replaces_streamed_english(self, post, configured, translate):
        post.return_value = _sse_response(['Use ', 'neem oil.'])
        response = self.client.post(reverse('chatbot:api_stream'),
                                    json.dumps({'message': 'How do I control aphids on chilli?', 'language': 'kn-IN'}),
                                    content_type='application/json')
        events = [json.loads(l) for l in b''.join(response.streaming_content).decode().splitlines() if l]
        replace = [e for e in events if e['type'] == 'replace']
        self.assertEqual(replace[0]['text'], 'ನೀಮ್ ಎಣ್ಣೆ ಬಳಸಿ')
        self.assertEqual(events[-1]['reply'], 'ನೀಮ್ ಎಣ್ಣೆ ಬಳಸಿ')

    def test_empty_message_is_rejected(self):
        response = self.client.post(reverse('chatbot:api_stream'), json.dumps({'message': ' '}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)


class StreamingEncodingTests(TestCase):
    @override_settings(GEMINI_API_KEY='test-placeholder')
    @patch('chatbot.engine.requests.post')
    def test_indian_language_text_is_not_garbled(self, post):
        """Gemini's SSE has no charset; without forcing UTF-8, Kannada came out as 'à²...'."""
        import io
        import requests
        kannada = 'ಭತ್ತಕ್ಕೆ ಯೂರಿಯಾ ಹಾಕಿ'
        raw = ('data: ' + json.dumps({'candidates': [{'content': {'parts': [{'text': kannada}]}}]},
                                     ensure_ascii=False) + '\n\n').encode('utf-8')
        resp = requests.models.Response()
        resp.status_code = 200
        resp.headers['Content-Type'] = 'text/event-stream'
        resp.raw = io.BytesIO(raw)
        post.return_value = resp
        self.assertEqual(''.join(engine.stream_gemini('paddy urea?', target_language='kn-IN')), kannada)


def _gemini_json(text):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {'candidates': [{'content': {'parts': [{'text': text}]}}]}
    return resp


@override_settings(GEMINI_API_KEY='test-placeholder', SARVAM_API_KEY='')
class ConversationMemoryTests(TestCase):
    """The assistant remembers the current chat until it is reset/closed."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def ask(self, message, url='chatbot:api'):
        response = self.client.post(reverse(url), json.dumps({'message': message}), content_type='application/json')
        if url == 'chatbot:api_stream':
            b''.join(response.streaming_content)
        return response

    @staticmethod
    def sent_contents(post):
        return post.call_args.kwargs['json']['contents']

    @patch('chatbot.engine.requests.post')
    def test_follow_up_question_includes_earlier_turns(self, post):
        post.return_value = _gemini_json('Use neem oil spray every 7 days for aphids.')
        self.ask('How do I control aphids on my chilli crop?')
        self.assertEqual(len(self.sent_contents(post)), 1)          # first question: no history

        post.return_value = _gemini_json('About 5 ml per litre of water.')
        self.ask('How much should I mix per litre?')
        contents = self.sent_contents(post)
        self.assertEqual([c['role'] for c in contents], ['user', 'model', 'user'])
        self.assertIn('aphids on my chilli', contents[0]['parts'][0]['text'])
        self.assertIn('neem oil', contents[1]['parts'][0]['text'])
        self.assertIn('How much should I mix', contents[2]['parts'][0]['text'])

    @patch('chatbot.engine.requests.post')
    def test_streaming_chat_also_remembers(self, post):
        post.return_value = _gemini_json('Late blight needs a copper fungicide.')
        self.ask('My tomato leaves have dark wet patches, what is it?')
        stream = MagicMock(status_code=200, text='')
        stream.iter_lines.return_value = ['data: ' + json.dumps({'candidates': [{'content': {'parts': [{'text': 'Every 10 days.'}]}}]})]
        post.return_value = stream
        self.ask('How often should I spray it?', url='chatbot:api_stream')
        self.assertEqual([c['role'] for c in self.sent_contents(post)], ['user', 'model', 'user'])

    @patch('chatbot.engine.requests.post')
    def test_follow_up_is_not_answered_from_another_chats_cache(self, post):
        from django.core.cache import cache
        cache.set(engine._reply_cache_key('How much should I mix per litre?', 'en-IN'), 'CACHED UNRELATED', 3600)
        post.return_value = _gemini_json('Use neem oil.')
        self.ask('How do I control aphids on my chilli crop?')
        post.return_value = _gemini_json('About 5 ml per litre.')
        reply = self.ask('How much should I mix per litre?').json()['reply']
        self.assertEqual(reply, 'About 5 ml per litre.')

    @patch('chatbot.engine.requests.post')
    def test_reset_ends_the_conversation(self, post):
        post.return_value = _gemini_json('Use neem oil.')
        self.ask('How do I control aphids on my chilli crop?')
        self.client.post(reverse('chatbot:clear'))
        post.return_value = _gemini_json('Fresh answer.')
        self.ask('What fertilizer suits paddy in Karnataka?')
        self.assertEqual(len(self.sent_contents(post)), 1)

    @patch('chatbot.engine.requests.post')
    def test_old_messages_are_not_remembered(self, post):
        from datetime import timedelta
        from django.utils import timezone
        post.return_value = _gemini_json('Use neem oil.')
        self.ask('How do I control aphids on my chilli crop?')
        ChatMessage.objects.update(created_at=timezone.now() - timedelta(hours=3))
        post.return_value = _gemini_json('Fresh answer.')
        self.ask('What fertilizer suits paddy in Karnataka?')
        self.assertEqual(len(self.sent_contents(post)), 1)


@override_settings(GEMINI_API_KEY='test-placeholder', SARVAM_API_KEY='test-key')
class GeminiTranslationTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    @patch('chatbot.translation.requests.post')
    def test_gemini_translates_and_result_is_cached(self, post):
        from . import translation
        post.return_value = _gemini_json('ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ')
        self.assertEqual(translation.translate('Spray neem oil', 'en-IN', 'kn-IN'), 'ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ')
        translation.translate('Spray neem oil', 'en-IN', 'kn-IN')
        self.assertEqual(post.call_count, 1)                              # second time from cache
        prompt = post.call_args.kwargs['json']['system_instruction']['parts'][0]['text']
        self.assertIn('kn-IN', prompt)

    @patch.object(sarvam, 'translate', return_value='ಸರ್ವಮ್ ಅನುವಾದ')
    @patch('chatbot.translation.requests.post', side_effect=__import__('requests').ConnectionError())
    def test_falls_back_to_sarvam_when_gemini_fails(self, post, sarvam_translate):
        from . import translation
        self.assertEqual(translation.translate('Spray neem oil', 'en-IN', 'kn-IN'), 'ಸರ್ವಮ್ ಅನುವಾದ')

    @patch.object(sarvam, 'translate', side_effect=sarvam.SarvamError('No credits available'))
    @patch('chatbot.translation.requests.post')
    def test_untranslated_echo_counts_as_failure(self, post, sarvam_translate):
        from . import translation
        post.return_value = _gemini_json('Spray neem oil')                # Gemini returned English
        with self.assertRaises(sarvam.SarvamError):
            translation.translate('Spray neem oil', 'en-IN', 'kn-IN')

    @patch('chatbot.translation.requests.post')
    def test_detect_language_accepts_only_known_codes(self, post):
        from . import translation
        post.return_value = _gemini_json('kn-IN')
        self.assertEqual(translation.detect_language('ನಮಸ್ಕಾರ'), 'kn-IN')
        post.return_value = _gemini_json('Klingon')
        self.assertEqual(translation.detect_language('qapla'), 'en-IN')

