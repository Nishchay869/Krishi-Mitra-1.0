from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_register_creates_farmer_profile_and_logs_in(self):
        resp = self.client.post(reverse('accounts:register'), {
            'email': 'ramesh@example.com', 'first_name': 'Ramesh', 'password1': 'Kh3t1-secure!', 'password2': 'Kh3t1-secure!',
            'district': 'Mandya', 'state': 'Karnataka', 'preferred_language': 'kn',
        })
        self.assertRedirects(resp, reverse('accounts:dashboard'))
        user = User.objects.get(email='ramesh@example.com')
        self.assertEqual(user.profile.role, 'farmer')
        self.assertEqual(user.profile.location_query, 'Mandya')

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_admin_dashboard_restricted_to_admins(self):
        User.objects.create_user('farmer', password='pw')
        self.client.login(username='farmer', password='pw')
        self.assertEqual(self.client.get(reverse('accounts:admin_dashboard')).status_code, 302)

        User.objects.create_user('officer', password='pw', is_staff=True)
        self.client.login(username='officer', password='pw')
        self.assertEqual(self.client.get(reverse('accounts:admin_dashboard')).status_code, 200)
        self.assertRedirects(self.client.get(reverse('accounts:dashboard')), reverse('accounts:admin_dashboard'))


class ProfileTests(TestCase):
    def test_profile_updates_name_used_for_greeting(self):
        user = User.objects.create_user('farmer', password='pw', first_name='old')
        self.client.force_login(user)
        self.assertContains(self.client.get(reverse('accounts:profile')), 'value="old"')
        self.client.post(reverse('accounts:profile'), {'first_name': 'Nishchay', 'preferred_language': 'kn'})
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Nishchay')
        self.assertEqual(user.profile.preferred_language, 'kn')


class SettingsTests(TestCase):
    def test_settings_page_renders_sections(self):
        resp = self.client.get(reverse('accounts:settings'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Select your Krishi Mitra Language')
        self.assertContains(resp, 'App Country')
        self.assertContains(resp, 'Information about my crops')
        self.assertContains(resp, 'Receive push notification')
        self.assertContains(resp, 'Weather temperature units')
        self.assertContains(resp, 'Celsius')
        self.assertContains(resp, 'Fahrenheit')
        self.assertContains(resp, 'Kelvin')

    def test_settings_post_updates_language_and_cookie(self):
        user = User.objects.create_user('settings_farmer', password='pw')
        self.client.force_login(user)
        resp = self.client.post(reverse('accounts:settings'), {
            'preferred_language': 'ta',
            'app_country': 'IN',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.profile.preferred_language, 'ta')
        self.assertEqual(self.client.cookies.get('django_language').value, 'ta')

    def test_settings_api_updates_language_asynchronously(self):
        user = User.objects.create_user('api_farmer', password='pw')
        self.client.force_login(user)
        resp = self.client.post(
            reverse('accounts:settings_api'),
            data={'preferred_language': 'kn'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['success'])
        user.refresh_from_db()
        self.assertEqual(user.profile.preferred_language, 'kn')


class FeedbackTests(TestCase):
    def test_submit_feedback_authenticated(self):
        user = User.objects.create_user('feedback_user', password='pw')
        self.client.force_login(user)
        resp = self.client.post(
            reverse('accounts:submit_feedback'),
            data={'rating': 'good', 'comment': 'Great application!'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['rating'], 'good')

        from accounts.models import Feedback
        fb = Feedback.objects.get(id=data['id'])
        self.assertEqual(fb.user, user)
        self.assertEqual(fb.rating, 'good')
        self.assertEqual(fb.comment, 'Great application!')

    def test_submit_feedback_anonymous(self):
        resp = self.client.post(
            reverse('accounts:submit_feedback'),
            data={'rating': 'average'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

        from accounts.models import Feedback
        fb = Feedback.objects.get(id=data['id'])
        self.assertIsNone(fb.user)
        self.assertEqual(fb.rating, 'average')

    def test_submit_feedback_invalid_rating(self):
        resp = self.client.post(
            reverse('accounts:submit_feedback'),
            data={'rating': 'terrible'},
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['success'])

    def test_admin_dashboard_shows_feedback_data(self):
        from accounts.models import Feedback
        Feedback.objects.create(rating='good')
        Feedback.objects.create(rating='average')
        Feedback.objects.create(rating='bad')

        admin_user = User.objects.create_user('admin_fb', password='pw', is_staff=True)
        self.client.force_login(admin_user)

        resp = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['feedback_count'], 3)
        self.assertEqual(resp.context['feedback_ratings']['good'], 1)
        self.assertEqual(resp.context['feedback_ratings']['average'], 1)
        self.assertEqual(resp.context['feedback_ratings']['bad'], 1)
        self.assertContains(resp, 'User App Experience Feedback')

    def test_login_two_portals_farmer_and_admin(self):
        farmer = User.objects.create_user('farmer_john', email='farmer@test.com', password='Password-123!')
        farmer.profile.role = 'farmer'
        farmer.profile.save()

        admin = User.objects.create_user('admin_jane', email='admin@test.com', password='Password-123!', is_staff=True)
        admin.profile.role = 'admin'
        admin.profile.save()

        # 1. Farmer logging in via Farmer portal -> success
        resp = self.client.post(reverse('accounts:login'), {
            'email': 'farmer@test.com',
            'password': 'Password-123!',
            'portal': 'farmer'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('accounts:dashboard'))
        self.client.logout()

        # 2. Farmer trying to log in via Admin portal -> rejected with message
        resp = self.client.post(reverse('accounts:login'), {
            'email': 'farmer@test.com',
            'password': 'Password-123!',
            'portal': 'admin'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Access denied')
        self.assertNotIn('_auth_user_id', self.client.session)

        # 3. Admin logging in via Admin portal -> redirects to admin dashboard
        resp = self.client.post(reverse('accounts:login'), {
            'email': 'admin@test.com',
            'password': 'Password-123!',
            'portal': 'admin'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('accounts:admin_dashboard'))

    def test_admin_crop_status_upload_and_delete(self):
        from crops.models import CropStatus
        admin = User.objects.create_user('agronomist', email='agro@test.com', password='Password-123!', is_staff=True)
        self.client.force_login(admin)

        # Upload a status
        resp = self.client.post(reverse('accounts:admin_upload_status'), {
            'crop_name': 'Tomato',
            'crop_slug': 'tomato',
            'title': 'Early Blight Warning',
            'caption': 'Inspect lower leaves for dark concentric ring spots.',
            'badge': 'alert',
            'duration_hours': '24',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('accounts:admin_dashboard'))

        status_obj = CropStatus.objects.filter(crop_slug='tomato').first()
        self.assertIsNotNone(status_obj)
        self.assertEqual(status_obj.title, 'Early Blight Warning')
        self.assertEqual(status_obj.badge, 'alert')

        # Check admin dashboard lists the active story
        dash_resp = self.client.get(reverse('accounts:admin_dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, 'Early Blight Warning')

        # Delete the status
        del_resp = self.client.post(reverse('accounts:admin_delete_status', args=[status_obj.id]))
        self.assertEqual(del_resp.status_code, 302)
        self.assertEqual(CropStatus.objects.filter(crop_slug='tomato').count(), 0)

    def test_home_page_surfaces_crop_status_stories(self):
        from crops.models import CropStatus
        user = User.objects.create_user('farm_user', password='pw')
        user.profile.selected_crops = ['Tomato', 'Rice']
        user.profile.save()
        self.client.force_login(user)

        CropStatus.objects.create(
            crop_name='Tomato',
            crop_slug='tomato',
            title='Late Blight Advisory',
            caption='Apply copper fungicide before morning dew.',
            badge='advisory',
            is_active=True,
        )

        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        user_crops = resp.context['user_crops']
        tomato_crop = next((c for c in user_crops if c['id'] == 'tomato'), None)
        self.assertIsNotNone(tomato_crop)
        self.assertTrue(tomato_crop.get('has_story'))
        self.assertTrue(tomato_crop.get('has_ring'))
        self.assertEqual(len(tomato_crop.get('stories', [])), 1)
        self.assertEqual(tomato_crop['stories'][0]['title'], 'Late Blight Advisory')


