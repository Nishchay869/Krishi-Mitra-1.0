from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from .forms import RegisterForm


class EmailAccountTests(TestCase):
    def signup(self, **changes):
        data = {'email': 'farmer@example.com', 'first_name': 'Farmer',
                'password1': 'Email-farm-934!', 'password2': 'Email-farm-934!',
                'state': 'Karnataka', 'district': 'Mandya', 'preferred_language': 'en'}
        data.update(changes)
        return self.client.post('/accounts/register/?stage=details', data)

    def test_signup_has_no_username_and_logs_in_by_email(self):
        self.assertNotIn('username', RegisterForm().fields)
        response = self.signup(email='Farmer@Example.COM')
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email='farmer@example.com')
        self.assertEqual(user.profile.district, 'Mandya')
        self.assertEqual(user.profile.state, 'Karnataka')
        self.client.logout()
        response = self.client.post('/accounts/login/', {'email':'FARMER@example.com', 'password':'Email-farm-934!'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_duplicate_email_rejected_case_insensitively(self):
        User.objects.create_user('legacy', email='Farmer@example.com', password='pw')
        response = self.signup(email='FARMER@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email already exists.')
        self.assertEqual(User.objects.count(), 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user('second', email='farmer@example.com')

    def test_wrong_state_district_pair_and_unknown_state_rejected(self):
        self.assertEqual(self.signup(state='Maharashtra').status_code, 200)
        self.assertEqual(self.signup(state='Imaginary state').status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_password_error_retains_locations(self):
        response = self.signup(password2='not-matching')
        form = response.context['form']
        self.assertEqual(form['state'].value(), 'Karnataka')
        self.assertEqual(form['district'].value(), 'Mandya')
        self.assertIn(('Mandya','Mandya'), list(form.fields['district'].choices))

    def test_login_rejects_username_wrong_password_and_inactive_account(self):
        user = User.objects.create_user('legacy', email='legacy@example.com', password='Email-farm-934!')
        for data in [{'username':'legacy','password':'Email-farm-934!'},
                     {'email':'legacy','password':'Email-farm-934!'},
                     {'email':'legacy@example.com','password':'wrong'},
                     {'email':'missing@example.com','password':'Email-farm-934!'}]:
            self.assertEqual(self.client.post('/accounts/login/', data).status_code, 200)
            self.assertNotIn('_auth_user_id', self.client.session)
        user.is_active = False;user.save()
        self.assertEqual(self.client.post('/accounts/login/', {'email':user.email,'password':'Email-farm-934!'}).status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_can_add_email_to_legacy_account(self):
        user = User.objects.create_user('legacy', password='Email-farm-934!')
        self.client.force_login(user)
        self.client.post('/accounts/profile/', {'email':'Legacy@Example.com','first_name':'Farmer','preferred_language':'en'})
        user.refresh_from_db()
        self.assertEqual(user.email, 'legacy@example.com')
        self.client.logout()
        response = self.client.post('/accounts/login/', {'email':user.email,'password':'Email-farm-934!'})
        self.assertEqual(response.status_code, 302)

    def test_next_redirect_cannot_escape_site(self):
        user = User.objects.create_user('legacy', email='legacy@example.com', password='Email-farm-934!')
        response = self.client.post('/accounts/login/', {'email':user.email,'password':'Email-farm-934!', 'next':'https://example.org/'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('example.org', response['Location'])
