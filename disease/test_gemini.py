import base64
import io
import json
from unittest.mock import Mock, patch

import requests
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from PIL import Image

from .gemini import DiagnosisError, analyze_leaf, normalize
from .views import api_detect, detect_page


def photo(size=(400, 300)):
    buffer = io.BytesIO()
    Image.new('RGB', size, '#4c853a').save(buffer, 'PNG')
    return SimpleUploadedFile('leaf.png', buffer.getvalue(), content_type='image/png')


def assessment(**updates):
    result = {
        'status': 'likely_disease', 'plant': 'Tomato', 'condition': 'Possible fungal leaf spot',
        'certainty': 'high', 'photo_quality': 'usable', 'crop_match': 'match',
        'summary': 'The visible spots could be consistent with a fungal issue.',
        'observations': ['Dark spots on the lower leaves.'],
        'possible_causes': ['Similar marks can occur with environmental stress.'],
        'immediate_actions': ['Inspect neighbouring plants and record whether spots are spreading.'],
        'prevention': ['Avoid prolonged leaf wetness.'],
        'follow_up': ['Confirm the cause with your local KVK.'],
        'chemical_options': [{'active_ingredient': 'Copper hydroxide', 'purpose': 'A potential protective option for a locally confirmed target.'}],
    }
    result.update(updates)
    return result


def provider_response(data=None, status=200, reason='STOP'):
    response = Mock(status_code=status)
    response.json.return_value = {'status': 'completed' if reason == 'STOP' else 'incomplete', 'steps': [{'type': 'model_output', 'content': [{'type': 'text', 'text': json.dumps(data or assessment())}]}]}
    return response


@override_settings(GEMINI_API_KEY='test-server-only-key', GEMINI_DISEASE_MODEL='gemini-3.8-flash')
class GeminiAssessmentTests(SimpleTestCase):
    @patch('disease.gemini.requests.post')
    def test_image_context_and_key_sent_server_side(self, post):
        post.return_value = provider_response()
        result = analyze_leaf(photo((2500, 1500)), crop='Tomato', location='Karnataka', notes='Lower leaves affected', language='kn')
        self.assertEqual(result['provider'], 'gemini')
        self.assertNotIn('confidence', result)
        self.assertEqual(len(result['chemical_options']), 1)
        args, kwargs = post.call_args
        self.assertNotIn('test-server-only-key', args[0])
        self.assertEqual(kwargs['headers']['x-goog-api-key'], 'test-server-only-key')
        self.assertFalse(kwargs['allow_redirects'])
        parts = kwargs['json']['input']
        self.assertFalse(kwargs['json']['store'])
        with Image.open(io.BytesIO(base64.b64decode(parts[0]['data']))) as image:
            self.assertLessEqual(max(image.size), 2048)
            self.assertEqual(image.format, 'JPEG')
            self.assertFalse(image.getexif())
        self.assertIn('Karnataka', parts[1]['text'])
        self.assertIn('kn', parts[1]['text'])

    def test_chemicals_withheld_when_uncertain_healthy_nonleaf_or_conflicting(self):
        for updates in [dict(status='healthy'), dict(status='not_leaf'), dict(status='uncertain'), dict(certainty='low'), dict(certainty='medium'), dict(photo_quality='unclear'), dict(crop_match='conflict')]:
            with self.subTest(updates=updates):
                self.assertEqual(normalize(assessment(**updates))['chemical_options'], [])
        self.assertEqual(normalize(assessment(photo_quality='unclear'))['status'], 'uncertain')

    def test_rejects_invented_doses_and_invalid_shapes(self):
        for updates in [dict(immediate_actions=['Spray 2 g per litre.']), dict(chemical_options=[{'active_ingredient': 'Copper hydroxide', 'purpose': 'Use 2 ml/L.'}]), dict(certainty='99%'), dict(observations='not a list')]:
            with self.subTest(updates=updates), self.assertRaises(DiagnosisError):
                normalize(assessment(**updates))
        self.assertTrue(normalize(assessment(observations=['About 20% of the visible leaf is marked.']))['observations'])

    @override_settings(GEMINI_API_KEY='')
    @patch('disease.gemini.requests.post')
    def test_missing_key_makes_no_external_request(self, post):
        with self.assertRaises(DiagnosisError) as error:
            analyze_leaf(photo())
        self.assertEqual(error.exception.code, 'not_configured')
        post.assert_not_called()

    @patch('disease.gemini.requests.post')
    def test_small_photo_not_sent(self, post):
        with self.assertRaises(DiagnosisError) as error:
            analyze_leaf(photo((64, 64)))
        self.assertEqual(error.exception.status, 422)
        post.assert_not_called()

    @patch('disease.gemini.requests.post')
    def test_upstream_failures_are_actionable_and_never_use_cnn(self, post):
        for status, code in [(403, 'access'), (429, 'quota'), (404, 'model_unavailable'), (500, 'upstream')]:
            post.return_value = provider_response(status=status)
            with self.subTest(status=status), self.assertRaises(DiagnosisError) as error:
                analyze_leaf(photo())
            self.assertEqual(error.exception.code, code)
        post.side_effect = requests.Timeout()
        with self.assertRaises(DiagnosisError) as error:
            analyze_leaf(photo())
        self.assertEqual(error.exception.status, 504)

    @patch('disease.gemini.requests.post')
    def test_blocked_truncated_and_malformed_outputs_rejected(self, post):
        post.return_value = provider_response(reason='MAX_TOKENS')
        with self.assertRaises(DiagnosisError):
            analyze_leaf(photo())
        post.return_value = provider_response()
        post.return_value.json.return_value = {'status': 'completed', 'steps': [{'type': 'model_output', 'content': [{'type': 'text', 'text': 'not JSON'}]}]}
        with self.assertRaises(DiagnosisError):
            analyze_leaf(photo())

    def test_result_is_escaped_in_template(self):
        result = normalize(assessment(summary='<script>alert(1)</script>'))
        html = render_to_string('disease/detect.html', {'result': result, 'user': AnonymousUser()})
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('Pesticide & spray recommendations', html)


class GeminiViewTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def request(self):
        request = self.factory.post('/disease/api/', {'image': photo(), 'crop': 'Tomato', 'location': 'Mysuru', 'notes': 'Two plants affected'})
        request.user = AnonymousUser()
        request.LANGUAGE_CODE = 'kn'
        return request

    @patch('disease.views.PredictionLog.objects.create')
    @patch('disease.views.analyze_leaf')
    def test_api_passes_context_and_keeps_dashboard_result_fields(self, analyze, save):
        analyze.return_value = normalize(assessment())
        response = api_detect(self.request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(analyze.call_args.kwargs['language'], 'kn')
        self.assertEqual(analyze.call_args.kwargs['crop'], 'Tomato')
        self.assertEqual(save.call_args.kwargs['result']['provider'], 'gemini')
        self.assertIn('treatment', json.loads(response.content))

    @patch('disease.views.PredictionLog.objects.create')
    @patch('disease.views.analyze_leaf')
    def test_api_quota_error_does_not_write_prediction(self, analyze, save):
        analyze.side_effect = DiagnosisError('Wait for quota', 'quota', 429)
        response = api_detect(self.request())
        self.assertEqual(response.status_code, 429)
        self.assertEqual(json.loads(response.content)['code'], 'quota')
        save.assert_not_called()

    @patch('disease.views.PredictionLog.objects.create')
    @patch('disease.views.analyze_leaf')
    def test_rate_limit_stops_provider_calls(self, analyze, save):
        analyze.return_value = normalize(assessment())
        for _ in range(6):
            self.assertEqual(api_detect(self.request()).status_code, 200)
        self.assertEqual(api_detect(self.request()).status_code, 429)
        self.assertEqual(analyze.call_count, 6)

    @patch('disease.views.analyze_leaf')
    def test_invalid_upload_never_calls_gemini(self, analyze):
        request = self.factory.post('/disease/api/', {'image': SimpleUploadedFile('fake.jpg', b'not an image', content_type='image/jpeg')})
        request.user = AnonymousUser()
        self.assertEqual(api_detect(request).status_code, 400)
        analyze.assert_not_called()
