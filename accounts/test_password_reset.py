import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class PasswordResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('farmer', email='farmer@example.com', password='old-Pass-123!')

    def test_full_reset_flow_changes_password(self):
        response = self.client.post(reverse('accounts:password_reset'), {'email': 'farmer@example.com'})
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('farmer@example.com', mail.outbox[0].to)

        link = re.search(r'https?://[^/\s]+(/accounts/password-reset/\S+/)', mail.outbox[0].body).group(1)
        form_url = self.client.get(link, follow=True).redirect_chain[-1][0]  # token is swapped for a session key
        response = self.client.post(form_url, {'new_password1': 'new-Pass-456!', 'new_password2': 'new-Pass-456!'})
        self.assertRedirects(response, reverse('accounts:password_reset_complete'))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new-Pass-456!'))

    def test_unknown_email_does_not_reveal_accounts(self):
        response = self.client.post(reverse('accounts:password_reset'), {'email': 'nobody@example.com'})
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_link_shows_message(self):
        response = self.client.get(reverse('accounts:password_reset_confirm', args=['bad', 'bad-token']))
        self.assertContains(response, 'invalid or has expired')

    def test_login_page_links_to_reset(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertContains(response, reverse('accounts:password_reset'))
