import io
import json
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from .predictor import predict, DiagnosisError
from .treatments import advice_for, parse_class, get_diagnosis_details
from .views import _run
from accounts.models import PredictionLog


class TreatmentTests(SimpleTestCase):
    def test_parses_plantvillage_class_names(self):
        self.assertEqual(parse_class('Tomato___Late_blight'), ('Tomato', 'late blight'))
        self.assertEqual(parse_class('Corn_(maize)___Common_rust_'), ('Corn (maize)', 'common rust'))

    def test_disease_gets_actionable_treatment(self):
        advice = advice_for('Potato___Early_blight')
        self.assertFalse(advice['is_healthy'])
        self.assertIn('mancozeb', advice['treatment'])

    def test_healthy_leaf(self):
        advice = advice_for('Apple___healthy')
        self.assertTrue(advice['is_healthy'])
        self.assertEqual(advice['disease'], 'Healthy')

    def test_unknown_disease_falls_back_to_kvk(self):
        self.assertIn('Krishi Vigyan Kendra', advice_for('Mango___Mystery_spot')['treatment'])


class MLModelInferenceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _sample_leaf_image(self, color=(60, 140, 40)):
        buf = io.BytesIO()
        Image.new('RGB', (120, 120), color).save(buf, format='JPEG')
        buf.seek(0)
        return SimpleUploadedFile('sample_leaf.jpg', buf.getvalue(), content_type='image/jpeg')

    def test_predict_runs_locally_with_cnn(self):
        image = self._sample_leaf_image()
        result = predict(image, crop='Tomato', location='Mandya', notes='Leaves curling')

        self.assertEqual(result['provider'], 'ml')
        self.assertEqual(result['model'], 'disease_cnn.keras')
        self.assertIn(result['status'], ('likely_disease', 'healthy', 'needs_confirmation'))
        self.assertIn(result['certainty'], ('high', 'medium', 'low'))
        self.assertIsInstance(result['confidence'], float)
        self.assertTrue(len(result['immediate_actions']) > 0)
        self.assertTrue(len(result['symptoms']) > 0)
        self.assertIn('treatment', result)
        self.assertIn('summary', result)

    def test_invalid_image_raises_diagnosis_error(self):
        corrupted = SimpleUploadedFile('corrupt.jpg', b'not a valid image byte stream', content_type='image/jpeg')
        with self.assertRaises(DiagnosisError) as ctx:
            predict(corrupted)
        self.assertEqual(ctx.exception.code, 'invalid_image')
        self.assertEqual(ctx.exception.status, 400)

    def test_all_classes_have_rich_metadata(self):
        classes_path = settings.BASE_DIR / 'ml' / 'models' / 'disease_classes.json'
        classes = json.loads(classes_path.read_text())
        self.assertGreater(len(classes), 0)  # class count changes whenever the model is retrained

        for c in classes:
            details = get_diagnosis_details(c, confidence=0.92)
            self.assertIn(details['disease_type'], ('fungal', 'bacterial', 'viral', 'pest', 'healthy'))
            self.assertTrue(len(details['summary']) > 0)
            self.assertTrue(len(details['immediate_actions']) > 0)
            self.assertTrue(len(details['cultural_control']) > 0)
            self.assertTrue(len(details['prevention']) > 0)

    @patch('disease.gemini.analyze_leaf', side_effect=DiagnosisError('quota', 'quota', 429))
    def test_views_run_saves_prediction_log_with_ml_provider(self, _gemini):
        # Gemini unavailable -> the local model answers
        request = self.factory.post('/disease/')
        request.user = AnonymousUser()
        request.session = {}

        cleaned_data = {
            'image': self._sample_leaf_image(),
            'crop': 'Corn',
            'location': 'Mysuru',
            'notes': 'Lower leaf spots'
        }

        result = _run(request, cleaned_data)
        self.assertEqual(result['provider'], 'ml')

        log = PredictionLog.objects.get(pk=result['log_id'])
        self.assertEqual(log.kind, PredictionLog.KIND_DISEASE)
        self.assertEqual(log.inputs['provider'], 'ml')
        self.assertEqual(log.result['provider'], 'ml')
        self.assertEqual(log.inputs['crop'], 'Corn')
        self.assertTrue(log.inputs['image_url'].startswith('/media/diagnoses/'))


class HybridDiagnosisTests(SimpleTestCase):
    def _image(self):
        buf = io.BytesIO()
        Image.new('RGB', (256, 256), (60, 140, 50)).save(buf, format='JPEG')
        return SimpleUploadedFile('leaf.jpg', buf.getvalue(), content_type='image/jpeg')

    @patch('disease.predictor.predict')
    @patch('disease.gemini.analyze_leaf', return_value={'provider': 'gemini', 'summary': 'x'})
    def test_gemini_answer_is_used_first(self, gemini_call, local_call):
        from .hybrid import analyze_leaf
        result = analyze_leaf(self._image(), crop='Cotton')
        self.assertEqual(result['provider'], 'gemini')
        local_call.assert_not_called()

    @patch('disease.predictor.predict', return_value={'provider': 'ml', 'summary': 'Late blight.'})
    @patch('disease.gemini.analyze_leaf', side_effect=DiagnosisError('offline', 'connection'))
    def test_falls_back_to_local_model_when_gemini_unavailable(self, gemini_call, local_call):
        from .hybrid import analyze_leaf
        result = analyze_leaf(self._image(), crop='Tomato')
        self.assertEqual(result['provider'], 'ml')
        self.assertEqual(result['fallback_reason'], 'connection')
        self.assertIn('Offline model', result['summary'])

    @patch('disease.predictor.predict')
    @patch('disease.gemini.analyze_leaf', side_effect=DiagnosisError('too small', 'image_quality', 422))
    def test_photo_problems_are_not_retried_locally(self, gemini_call, local_call):
        from .hybrid import analyze_leaf
        with self.assertRaises(DiagnosisError):
            analyze_leaf(self._image())
        local_call.assert_not_called()
