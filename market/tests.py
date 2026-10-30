from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from . import services
from .services import compare, parse

PAYLOAD = {
    'status': 'success',
    'data': {
        'columns': [
            {'key': 'commodity_info', 'columns': []},
            {'key': 'price_group', 'columns': [
                {'key': 'as_on_price', 'title': '08 Oct, 2026'},
                {'key': 'one_day_ago_price', 'title': '07 Oct, 2026'},
                {'key': 'two_day_ago_price', 'title': '06 Oct, 2026'},
            ]},
        ],
        'records': [
            # Agmarknet's own "trend" says down although the price rose; we must ignore it.
            {'trend': 'down', 'cmdt_name': 'Paddy(Common)', 'cmdt_grp_name': 'Cereals', 'msp_price': '2441.00',
             'as_on_price': '2510.70', 'one_day_ago_price': '2469.34', 'two_day_ago_price': '2545.22',
             'as_on_arrival': '96813.69'},
            {'trend': 'up', 'cmdt_name': 'Tomato', 'cmdt_grp_name': 'Vegetables', 'msp_price': None,
             'as_on_price': '1619.88', 'one_day_ago_price': '1670.57', 'two_day_ago_price': None,
             'as_on_arrival': '500'},
            {'trend': None, 'cmdt_name': 'Niger Seed(Ramtil)', 'cmdt_grp_name': 'Oil Seeds', 'msp_price': '10052.00',
             'as_on_price': '11832.14', 'one_day_ago_price': None, 'two_day_ago_price': None, 'as_on_arrival': '1'},
        ],
    },
}


class ParseTests(SimpleTestCase):
    def test_compare(self):
        self.assertEqual(compare(110, 100), ('up', 10, 10.0))
        self.assertEqual(compare(90, 100), ('down', -10, -10.0))
        self.assertEqual(compare(100, 100), ('same', 0, 0.0))
        self.assertEqual(compare(100, None), ('na', None, None))

    def test_parse_computes_direction_from_prices_not_api_trend(self):
        result = parse(PAYLOAD)
        self.assertEqual(result['date'], date(2026, 10, 8))
        self.assertEqual(result['previous_date'], date(2026, 10, 7))
        paddy, tomato, niger = result['rows']
        self.assertEqual(paddy['direction'], 'up')
        self.assertEqual(paddy['change'], 41.36)
        self.assertEqual(paddy['vs_msp'], 'above')
        self.assertEqual(tomato['direction'], 'down')
        self.assertIsNone(tomato['vs_msp'])
        self.assertEqual(niger['direction'], 'na')


@patch.object(services, '_request')
class MarketViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user('farmer', password='pw')
        self.user.profile.state = 'Karnataka'
        self.user.profile.save()
        self.client.force_login(self.user)

    def _fake(self, calls):
        def fake(method, path, **kwargs):
            calls.append((path, kwargs.get('json')))
            if path.startswith('daily-price-arrival/filters'):
                return {'data': {'state_data': [{'state_id': 100000, 'state_name': 'All States/UTs'},
                                                {'state_id': 16, 'state_name': 'Karnataka'}]}}
            return PAYLOAD
        return fake

    def test_page_defaults_to_profile_state_and_shows_arrows(self, mock_request):
        calls = []
        mock_request.side_effect = self._fake(calls)
        resp = self.client.get(reverse('market:overview'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(calls[-1][1]['state'], 16)
        html = resp.content.decode()
        self.assertIn('Daily mandi prices — Karnataka', html)
        self.assertIn('price-up', html)
        self.assertIn('price-down', html)
        self.assertEqual(resp.context['summary'], {'up': 1, 'down': 1, 'flat': 1})
        self.assertEqual(resp.context['days_old'], (date.today() - date(2026, 10, 8)).days)

    def test_all_india_selection(self, mock_request):
        calls = []
        mock_request.side_effect = self._fake(calls)
        resp = self.client.get(reverse('market:overview'), {'state': '0'})
        self.assertNotIn('state', calls[-1][1])
        self.assertEqual(resp.context['state_name'], 'All India')

    def test_api_and_service_failure(self, mock_request):
        mock_request.side_effect = self._fake([])
        data = self.client.get(reverse('market:api'), {'state': 16}).json()
        self.assertEqual(data['unit'], 'Rs/quintal')
        self.assertEqual(data['prices'][0]['direction'], 'up')

        cache.clear()
        mock_request.side_effect = services.MarketError('down')
        self.assertEqual(self.client.get(reverse('market:api')).status_code, 502)
        self.assertContains(self.client.get(reverse('market:overview')), 'down')
