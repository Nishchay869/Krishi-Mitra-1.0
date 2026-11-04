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

    def test_recommends_wheat_for_punjab_conditions(self):
        punjab_cond = {'N': 120, 'P': 50, 'K': 40, 'temperature': 19.5, 'humidity': 58, 'ph': 6.8, 'rainfall': 65}
        resp = self.client.post(reverse('crops:api'), json.dumps(punjab_cond), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        recs = resp.json()['recommendations']
        self.assertEqual(recs[0]['crop'], 'wheat')
        self.assertEqual(recs[0]['name'], 'Wheat (Gehun)')
        self.assertEqual(recs[0]['hindi_name'], 'गेहूं')
        self.assertEqual(recs[0]['emoji'], '🌾')
        self.assertIn('alluvial', recs[0]['why_message'].lower())

    def test_recommends_bajra_for_arid_conditions(self):
        arid_cond = {'N': 68, 'P': 35, 'K': 25, 'temperature': 31.0, 'humidity': 42, 'ph': 7.4, 'rainfall': 38}
        resp = self.client.post(reverse('crops:api'), json.dumps(arid_cond), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        recs = resp.json()['recommendations']
        self.assertEqual(recs[0]['crop'], 'bajra')
        self.assertEqual(recs[0]['category'], 'Millet')

    def test_recommend_page_renders_with_presets_and_results(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='farmer1', password='testpassword123')
        self.client.login(username='farmer1', password='testpassword123')
        resp = self.client.get(reverse('crops:recommend'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'One-Tap Regional Soil & Climate Presets')
        self.assertContains(resp, 'Indo-Gangetic Alluvial Belt')

        # Submit POST form
        punjab_cond = {'N': 120, 'P': 50, 'K': 40, 'temperature': 19.5, 'humidity': 58, 'ph': 6.8, 'rainfall': 65}
        post_resp = self.client.post(reverse('crops:recommend'), punjab_cond)
        self.assertEqual(post_resp.status_code, 200)
        self.assertContains(post_resp, 'Wheat (Gehun)')
        self.assertContains(post_resp, 'TOP RECOMMENDATION')


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
