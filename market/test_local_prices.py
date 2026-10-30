from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from unittest.mock import patch


@override_settings(DATA_GOV_IN_API_KEY='')
class LocalMandiTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('mandi-farmer')
        profile=self.user.profile
        profile.state='Karnataka'; profile.district='Bengaluru'
        profile.selected_crops=['Tomato'];profile.save()
        self.client.force_login(self.user)

    @patch('requests.request',side_effect=AssertionError('Setup UI must not call live price services'))
    def test_profile_location_and_crop_defaults(self, _):
        response=self.client.get('/market/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['state']['id'],16)
        self.assertEqual(response.context['district']['id'],243)
        self.assertEqual(response.context['crop']['name'],'Tomato')
        self.assertContains(response,'Binny Mill (FF&amp;V) Bengaluru APMC')
        self.assertContains(response,'Live local prices are not connected yet.')
        self.assertTrue(all(r['modal_price'] is None for r in response.context['cards']))

    def test_specific_market_crop_and_unit(self):
        response=self.client.get('/market/',{'state':16,'district':243,'market':100,'crop':23,'unit':'kg'})
        self.assertEqual(len(response.context['cards']),1)
        self.assertEqual(response.context['market']['id'],100)
        self.assertEqual(response.context['unit'],'kg')
        self.assertIn('maps/search/',response.context['cards'][0]['map_url'])

    def test_cross_state_district_and_market_are_rejected(self):
        response=self.client.get('/market/',{'state':16,'district':565,'market':-1,'unit':'bad'})
        self.assertIsNone(response.context['district'])
        self.assertIsNone(response.context['market'])
        self.assertEqual(response.context['unit'],'qtl')
        self.assertTrue(all(m['state']==16 for m in response.context['markets']))

    def test_empty_location_does_not_show_arbitrary_mandis(self):
        response=self.client.get('/market/',{'state':''})
        self.assertEqual(response.context['cards'],[])
        self.assertContains(response,'Select a location to view mandis.')

    def test_native_labels_and_login_requirement(self):
        self.user.profile.preferred_language='kn';self.user.profile.save()
        response=self.client.get('/market/')
        self.assertContains(response,'ಕನಿಷ್ಠ ಬೆಲೆ')
        self.client.logout()
        self.assertEqual(self.client.get('/market/').status_code,302)
