import json
import os
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import PredictionLog

User = get_user_model()

class DiagnosisHistoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='farmer_test',
            email='farmer@example.com',
            password='TestPassword123!',
            first_name='Farmer',
            last_name='Test',
        )
        self.other_user = User.objects.create_user(
            username='other_farmer',
            email='other@example.com',
            password='TestPassword123!',
        )
        self.client = Client()

        # Create sample prediction logs for self.user
        self.log1 = PredictionLog.objects.create(
            user=self.user,
            kind=PredictionLog.KIND_DISEASE,
            inputs={
                'crop': 'Tomato',
                'image_url': '/media/diagnoses/test_leaf1.jpg',
                'image_path': 'diagnoses/test_leaf1.jpg',
            },
            result={
                'status': 'likely_disease',
                'disease': 'Tomato Early Blight',
                'plant': 'Tomato',
                'certainty': 'high',
                'summary': 'Early blight caused by Alternaria solani.',
                'symptoms': ['Concentric rings on lower leaves', 'Yellowing halo'],
                'immediate_actions': ['Remove lower infected leaves'],
                'chemical_options': [
                    {'active_ingredient': 'Mancozeb 75% WP', 'purpose': 'Protective fungicide'}
                ],
            }
        )

        self.log2 = PredictionLog.objects.create(
            user=self.user,
            kind=PredictionLog.KIND_DISEASE,
            inputs={
                'crop': 'Chilli',
                'image_url': '/media/diagnoses/test_leaf2.jpg',
            },
            result={
                'status': 'uncertain',
                'disease': 'Uncertain cause',
                'plant': 'Chilli',
                'certainty': 'low',
                'summary': 'Photo unclear, please retake in good lighting.',
            }
        )

        # Log for other user
        self.other_log = PredictionLog.objects.create(
            user=self.other_user,
            kind=PredictionLog.KIND_DISEASE,
            inputs={'crop': 'Potato'},
            result={'status': 'likely_disease', 'disease': 'Late Blight'}
        )

    def test_history_page_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('disease:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tomato Early Blight')
        self.assertContains(response, 'Confirm a diagnosis')  # For uncertain status
        self.assertContains(response, 'Complete')
        self.assertContains(response, 'Incomplete')
        # Does not contain other user's records
        self.assertNotContains(response, 'Late Blight')

    def test_history_page_anonymous_session_user(self):
        # Set session history for anonymous user
        session = self.client.session
        session['diagnosis_history'] = [self.log1.id]
        session.save()

        response = self.client.get(reverse('disease:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tomato Early Blight')
        self.assertNotContains(response, 'Uncertain cause')

    def test_history_detail_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('disease:history_detail', args=[self.log1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tomato Early Blight')
        self.assertContains(response, 'Concentric rings on lower leaves')
        self.assertContains(response, 'Mancozeb 75% WP')

        # Cannot view other user's diagnosis
        resp_forbidden = self.client.get(reverse('disease:history_detail', args=[self.other_log.id]))
        self.assertEqual(resp_forbidden.status_code, 404)

    def test_delete_single_diagnosis(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('disease:delete_single', args=[self.log2.id]))
        self.assertRedirects(response, reverse('disease:history'))
        self.assertFalse(PredictionLog.objects.filter(id=self.log2.id).exists())
        self.assertTrue(PredictionLog.objects.filter(id=self.log1.id).exists())

    def test_delete_selected_diagnoses_form(self):
        self.client.force_login(self.user)
        # Select log1 and log2
        response = self.client.post(reverse('disease:delete_selected'), {
            'selected_ids': [str(self.log1.id), str(self.log2.id)]
        })
        self.assertRedirects(response, reverse('disease:history'))
        self.assertFalse(PredictionLog.objects.filter(id=self.log1.id).exists())
        self.assertFalse(PredictionLog.objects.filter(id=self.log2.id).exists())
        # Other user's log is untouched
        self.assertTrue(PredictionLog.objects.filter(id=self.other_log.id).exists())

    def test_delete_selected_diagnoses_json(self):
        self.client.force_login(self.user)
        payload = json.dumps({'selected_ids': [self.log1.id]})
        response = self.client.post(
            reverse('disease:delete_selected'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('deleted_count'), 1)
        self.assertFalse(PredictionLog.objects.filter(id=self.log1.id).exists())
        self.assertTrue(PredictionLog.objects.filter(id=self.log2.id).exists())

    def test_delete_all_diagnoses(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('disease:delete_all'))
        self.assertRedirects(response, reverse('disease:history'))
        self.assertEqual(PredictionLog.objects.filter(user=self.user).count(), 0)
        self.assertTrue(PredictionLog.objects.filter(id=self.other_log.id).exists())

    def test_home_page_shows_recent_diagnoses(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_diagnoses', response.context)
        self.assertEqual(len(response.context['recent_diagnoses']), 2)
        # Check rendered HTML
        self.assertContains(response, 'Tomato Early Blight')

