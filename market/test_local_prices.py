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


@override_settings(DATA_GOV_IN_API_KEY='test-key')
class BrowserFetchFallbackTests(TestCase):
    """data.gov.in refuses some servers (e.g. Render, outside India): browsers fetch instead."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user('browser-farmer')
        profile = self.user.profile
        profile.state = 'Karnataka'; profile.district = 'Bengaluru'
        profile.selected_crops = ['Tomato']; profile.save()
        self.client.force_login(self.user)

    def record(self, **over):
        from django.utils import timezone
        rec = {'state': 'Karnataka', 'district': 'Bangalore', 'market': 'Binny Mill (F&V), Bangalore',
               'commodity': 'Tomato', 'variety': 'Hybrid', 'grade': 'FAQ',
               'arrival_date': timezone.localdate().strftime('%d/%m/%Y'),
               'min_price': '800', 'modal_price': '1000', 'max_price': '1200'}
        rec.update(over)
        return rec

    def seed(self, records):
        import json
        return self.client.post('/market/browser-prices/', json.dumps(
            {'state': 'Karnataka', 'crop': 'Tomato', 'records': records}), content_type='application/json')

    @patch('market.provider.requests.get')
    def test_refused_server_asks_browser_to_fetch(self, get):
        import requests
        get.side_effect = requests.ConnectionError('refused')
        response = self.client.get('/market/', {'state': 16, 'crop': 65})
        cfg = response.context['browser_fetch']
        self.assertEqual((cfg['state'], cfg['crop'], cfg['api_key']), ('Karnataka', 'Tomato', 'test-key'))
        self.assertIsNone(response.context['error'])
        self.assertContains(response, 'mandi-browser-fetch-config')
        self.assertNotContains(response, 'No prices reported for this selection.')
        # second attempt after the browser tried: show the honest message, no loop
        again = self.client.get('/market/', {'state': 16, 'crop': 65, 'seeded': 1})
        self.assertIsNone(again.context['browser_fetch'])
        self.assertTrue(again.context['error'])

    @patch('market.provider.requests.get')
    def test_browser_records_are_validated_and_shown(self, get):
        import requests
        get.side_effect = requests.ConnectionError('refused')
        bad = self.record(state='Punjab')              # wrong state: rejected by parse_record
        response = self.seed([self.record(), bad, 'junk'])
        self.assertEqual(response.json(), {'ok': True, 'rows': 1})
        page = self.client.get('/market/', {'state': 16, 'crop': 65, 'seeded': 1, 'district': ''})
        self.assertIsNone(page.context['error'])
        self.assertEqual([c['modal_price'] for c in page.context['cards']], [1000])
        get.assert_not_called()  # served from the farmer's browser-fetched copy

    def test_browser_records_are_private_to_the_uploader(self):
        self.seed([self.record()])
        from market.provider import _browser_cache_key
        from django.core.cache import cache
        other = User.objects.create_user('other-farmer')
        self.assertIsNone(cache.get(_browser_cache_key(other.pk, 'Karnataka', 'Tomato')))

    def test_oversized_or_anonymous_uploads_rejected(self):
        self.assertEqual(self.seed([self.record()] * 1001).status_code, 400)
        self.client.logout()
        self.assertEqual(self.seed([self.record()]).status_code, 302)
