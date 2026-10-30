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
