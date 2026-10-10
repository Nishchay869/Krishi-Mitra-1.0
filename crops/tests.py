import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from unittest import skipUnless

from accounts.models import PredictionLog

MODEL_EXISTS = (settings.ML_MODELS_DIR / 'crop_rf.joblib').exists()
RICE_LIKE = {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.9, 'humidity': 82, 'ph': 6.5, 'rainfall': 203}


@skipUnless(MODEL_EXISTS, 'Run python -m ml.train_crop first')
class CropApiTests(TestCase):
    def test_recommends_rice_for_rice_conditions(self):
        resp = self.client.post(reverse('crops:api'), json.dumps(RICE_LIKE), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        recs = resp.json()['recommendations']
        self.assertEqual(recs[0]['crop'], 'rice')
        self.assertEqual(len(recs), 3)
        self.assertEqual(PredictionLog.objects.filter(kind='crop').count(), 1)

    def test_rejects_out_of_range_input(self):
        resp = self.client.post(reverse('crops:api'), json.dumps({**RICE_LIKE, 'ph': 20}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('ph', resp.json()['errors'])


YIELD_MODEL_EXISTS = (settings.ML_MODELS_DIR / 'yield_rf.joblib').exists()
PUNJAB_WHEAT = {'crop': 'Wheat', 'season': 'Rabi', 'state': 'Punjab', 'rainfall': 650, 'area_ha': 2}


@skipUnless(YIELD_MODEL_EXISTS, 'Run python -m ml.train_yield first')
class YieldApiTests(TestCase):
    def test_predicts_plausible_yield_with_range_and_total(self):
        resp = self.client.post(reverse('crops:yield_api'), json.dumps(PUNJAB_WHEAT), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(3 < data['yield_per_ha'] < 6, data)  # Punjab wheat is ~4-5 t/ha
        self.assertLessEqual(data['range_low'], data['yield_per_ha'])
        self.assertGreaterEqual(data['range_high'], data['yield_per_ha'])
        self.assertAlmostEqual(data['total'], data['yield_per_ha'] * 2, places=1)
        self.assertEqual(data['unit'], 'tonnes/ha')
        self.assertEqual(PredictionLog.objects.filter(kind='yield').count(), 1)

    def test_cotton_reported_in_bales(self):
        resp = self.client.post(reverse('crops:yield_api'), json.dumps(
            {'crop': 'Cotton(lint)', 'season': 'Kharif', 'state': 'Maharashtra', 'rainfall': 900}),
            content_type='application/json')
        self.assertIn('bales', resp.json()['unit'])

    def test_rejects_unknown_crop(self):
        resp = self.client.post(reverse('crops:yield_api'), json.dumps({**PUNJAB_WHEAT, 'crop': 'Dragonfruit'}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('crop', resp.json()['errors'])
