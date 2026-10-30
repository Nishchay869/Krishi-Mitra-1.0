from django.contrib.auth.models import User
from django.test import TestCase
from .languages import available_languages


class OnboardingTests(TestCase):
    def test_language_selection_applies_before_signup(self):
        response = self.client.post('/accounts/onboarding/', {'action': 'language', 'language': 'kn'}, follow=True)
        self.assertEqual(response['Content-Language'], 'kn')
        self.assertContains(response, '<html lang="kn"')
        self.assertContains(response, 'value="kn" selected')
        self.assertEqual(self.client.session['signup_language'], 'kn')
        self.assertEqual(len(available_languages()), 16)

    def test_unavailable_language_rejected(self):
        self.client.post('/accounts/onboarding/', {'action': 'language', 'language': 'ur'})
        self.assertNotIn('signup_language', self.client.session)

    def test_preferences_survive_signup_and_can_be_edited(self):
        self.client.post('/accounts/onboarding/', {'action': 'preferences', 'selected_crops': ['Rice', 'Tomato'], 'growing_place': 'field'})
        response = self.client.post('/accounts/register/?stage=details', {
            'email': 'onboard@example.com', 'state': 'Karnataka', 'district': 'Mandya', 'password1': 'Secure-farm-983!',
            'password2': 'Secure-farm-983!', 'preferred_language': 'en',
        }, follow=True)
        user = User.objects.get(email='onboard@example.com')
        self.assertEqual(user.profile.selected_crops, ['Rice', 'Tomato'])
        self.assertEqual(user.profile.growing_place, 'field')
        self.assertContains(response, 'Tomato')
        self.assertNotIn('farm_preferences', self.client.session)
        self.client.post('/accounts/profile/', {'preferred_language': 'en', 'selected_crops': ['Mango'], 'growing_place': 'pots'})
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.selected_crops, ['Mango'])
        self.assertEqual(user.profile.growing_place, 'pots')

    def test_invalid_preferences_do_not_enter_session(self):
        response = self.client.post('/accounts/onboarding/', {'selected_crops': ['invented'], 'growing_place': 'invalid'})
        self.assertRedirects(response, '/accounts/register/?stage=farm')
        self.assertNotIn('farm_preferences', self.client.session)

    def test_failed_registration_retains_details_and_preferences(self):
        self.client.post('/accounts/onboarding/', {'selected_crops': ['Rice'], 'growing_place': 'garden'})
        response = self.client.post('/accounts/register/', {'username': '', 'preferred_language': 'en'})
        self.assertContains(response, 'data-stage="details"')
        self.assertEqual(self.client.session['farm_preferences']['selected_crops'], ['Rice'])

    def test_all_stages_render_and_can_skip_preferences(self):
        for stage in ['language', 'tour', 'farm', 'growing', 'details']:
            response = self.client.get('/accounts/register/', {'stage': stage})
            self.assertEqual(response.status_code, 200)
        self.client.post('/accounts/onboarding/', {'action': 'preferences'})
        self.assertEqual(self.client.session['farm_preferences'], {'selected_crops': [], 'growing_place': ''})

    def test_post_requires_csrf(self):
        from django.test import Client
        self.assertEqual(Client(enforce_csrf_checks=True).post('/accounts/onboarding/', {'language': 'kn'}).status_code, 403)

    def test_crop_step_is_saved_before_growing_place(self):
        response = self.client.post('/accounts/onboarding/', {'action': 'crops', 'selected_crops': ['Rice']})
        self.assertRedirects(response, '/accounts/register/?stage=growing')
        self.assertEqual(self.client.session['farm_preferences']['selected_crops'], ['Rice'])

    def test_indian_crop_catalog_has_local_images_and_complete_translations(self):
        import json
        from pathlib import Path
        from django.conf import settings
        from .onboarding import CROP_GROUPS
        root = Path(settings.BASE_DIR)
        groups = dict(CROP_GROUPS)
        self.assertEqual(set(groups), {'Vegetables', 'Cereals', 'Pulses', 'Fruits', 'Oilseeds', 'Spices', 'Cash crops', 'Flowers'})
        crops = [name for _, items in CROP_GROUPS for name, _ in items]
        self.assertEqual(len(crops), len(set(crops)))
        self.assertIn('Jowar', crops)
        self.assertIn('Marigold', crops)
        for _, items in CROP_GROUPS:
            for name, image in items:
                self.assertTrue((root / 'static' / image).is_file(), name)
        for code, _ in available_languages():
            catalog = json.loads((root / 'locale/ui' / f'{code}.json').read_text())
            for label in [*groups, *crops]:
                self.assertTrue(catalog.get(label), f'{code}: {label}')

    def test_indian_crops_and_flowers_can_be_selected_together(self):
        selected = ['Brinjal', 'Jowar', 'Jackfruit', 'Marigold', 'Jasmine']
        self.client.post('/accounts/onboarding/', {'action': 'crops', 'selected_crops': selected})
        self.assertEqual(self.client.session['farm_preferences']['selected_crops'], selected)
