from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_register_creates_farmer_profile_and_logs_in(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'ramesh', 'first_name': 'Ramesh', 'password1': 'Kh3t1-secure!', 'password2': 'Kh3t1-secure!',
            'district': 'Mandya', 'state': 'Karnataka', 'preferred_language': 'kn',
        })
        self.assertRedirects(resp, reverse('accounts:dashboard'))
        user = User.objects.get(username='ramesh')
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
