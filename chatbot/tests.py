import json

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from . import engine
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
        self.assertEqual(engine.answer('will it rain tomorrow?').intent, 'weather')
        self.assertEqual(engine.answer('what is the jowar price today').intent, 'market')
        self.assertIsNotNone(engine.answer('how to sell crop online').entry)

    def test_unknown_question_falls_back(self):
        reply = engine.answer('quantum chromodynamics lattice gauge')
        self.assertIsNone(reply.entry)
        self.assertIn('Kisan Call Centre', reply.text)


class ChatApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_knowledge', verbosity=0)

    def test_api_returns_reply_and_logs_message(self):
        resp = self.client.post(reverse('chatbot:api'), json.dumps({'message': 'fertilizer dose for wheat'}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('120 kg N', data['reply'])
        self.assertTrue(data['source'])
        self.assertEqual(ChatMessage.objects.count(), 1)

    def test_api_rejects_empty_and_bad_json(self):
        url = reverse('chatbot:api')
        self.assertEqual(self.client.post(url, '{}', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(url, 'not json', content_type='application/json').status_code, 400)
