from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch
import requests
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from .provider import fetch_local_prices, parse_record, LocalPriceError

ROW={'state':'Karnataka','district':'Bengaluru','market':'Binny Mill (FF&V) Bengaluru APMC',
     'commodity':'Tomato','variety':'Tomato','grade':'Local','arrival_date':'28/10/2026',
     'min_price':'800','modal_price':'1000','max_price':'1500'}


def response(rows,total=None):
    result=Mock();result.json.return_value={'status':'ok','records':rows,'total':len(rows) if total is None else total}
    return result


@override_settings(DATA_GOV_IN_API_KEY='private-test-key')
class ProviderTests(SimpleTestCase):
    def setUp(self): cache.clear()

    @patch('market.provider.requests.get')
    def test_filters_cache_and_decimal_values(self,get):
        get.return_value=response([ROW])
        data=fetch_local_prices('Karnataka','Tomato')
        self.assertEqual(data['rows'][0]['modal_price'],Decimal('1000'))
        self.assertEqual(data['rows'][0]['date'],date(2026,10,28))
        self.assertEqual(get.call_args.kwargs['params']['filters[state]'],'Karnataka')
        self.assertEqual(get.call_args.kwargs['params']['filters[commodity]'],'Tomato')
        self.assertEqual(fetch_local_prices('Karnataka','Tomato'),data)
        self.assertEqual(get.call_count,1)

    def test_bad_records_never_become_prices(self):
        for changes in [{'state':'Punjab'},{'commodity':'Onion'},{'arrival_date':'bad'},
                        {'modal_price':'2000'},{'min_price':'2000'},{'market':''}]:
            self.assertIsNone(parse_record({**ROW,**changes},'Karnataka','Tomato'))
        record=parse_record({**ROW,'min_price':None},'Karnataka','Tomato')
        self.assertIsNone(record['min_price'])
        self.assertEqual(record['modal_price'],Decimal(1000))

    @patch('market.provider.requests.get')
    def test_pagination_and_latest_observation(self,get):
        get.side_effect=[response([{**ROW,'arrival_date':'27/10/2026'}],2),response([ROW],2)]
        result=fetch_local_prices('Karnataka','Tomato')
        self.assertEqual(len(result['rows']),1)
        self.assertEqual(result['rows'][0]['date'],date(2026,10,28))
        self.assertEqual(get.call_args.kwargs['params']['offset'],1)

    def test_future_dates_wrong_units_and_blank_market_are_rejected(self):
        from datetime import timedelta
        from django.utils import timezone
        future=(timezone.localdate()+timedelta(days=1)).strftime('%d/%m/%Y')
        for changes in [{'arrival_date':future},{'price_unit':'Rs/kg'},{'market':'  '}]:
            self.assertIsNone(parse_record({**ROW,**changes},'Karnataka','Tomato'))
        self.assertIsNotNone(parse_record({**ROW,'price_unit':'Rs./Quintal'},'Karnataka','Tomato'))

    @patch('market.provider.requests.get')
    def test_conflicting_same_report_is_withheld_regardless_of_order(self,get):
        for rows in [[ROW,{**ROW,'modal_price':'1100'}],[{**ROW,'modal_price':'1100'},ROW]]:
            cache.clear();get.return_value=response(rows)
            result=fetch_local_prices('Karnataka','Tomato')
            self.assertEqual(result['rows'],[])
            self.assertEqual(result['conflicts'],1)

    @patch('market.provider.requests.get')
    def test_newer_unambiguous_report_replaces_old_conflict(self,get):
        get.return_value=response([{**ROW,'arrival_date':'27/10/2026'},
            {**ROW,'arrival_date':'27/10/2026','modal_price':'1100'},ROW,ROW])
        result=fetch_local_prices('Karnataka','Tomato')
        self.assertEqual(len(result['rows']),1)
        self.assertEqual(result['rows'][0]['modal_price'],Decimal(1000))
        self.assertEqual(result['conflicts'],0)
        self.assertIsNotNone(result['fetched_at'])

    @patch('market.provider.requests.get')
    def test_errors_do_not_reveal_key_or_turn_into_empty_success(self,get):
        get.side_effect=requests.RequestException('url?api-key=private-test-key')
        with self.assertRaises(LocalPriceError) as ctx:fetch_local_prices('Karnataka','Tomato')
        self.assertNotIn('private-test-key',str(ctx.exception))
        get.side_effect=None;get.return_value=response([]);get.return_value.json.return_value={'status':'error','message':'Invalid API key'}
        with self.assertRaises(LocalPriceError):fetch_local_prices('Karnataka','Tomato')


@override_settings(DATA_GOV_IN_API_KEY='private-test-key')
@patch('market.local_prices.fetch_local_prices')
class LiveMandiViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('live-mandi')
        p=self.user.profile;p.state='Karnataka';p.district='Bengaluru';p.save()
        self.client.force_login(self.user)

    def data(self,mock):
        mock.return_value={'rows':[parse_record(ROW,'Karnataka','Tomato')],'truncated':False}

    def test_selected_market_actual_prices_and_unit_conversion(self,mock):
        self.data(mock)
        for unit,expected in [('qtl','1000'),('kg','10')]:
            page=self.client.get('/market/',{'state':16,'district':243,'market':100,'crop':65,'unit':unit})
            self.assertEqual(page.context['cards'][0]['modal_price'],Decimal(expected))
            self.assertContains(page,'28 Oct 2026')
            self.assertNotContains(page,'Live local prices are not connected yet.')
        self.assertEqual(mock.return_value['rows'][0]['modal_price'],Decimal(1000))

    def test_default_missing_district_shows_actual_state_markets_with_notice(self,mock):
        mock.return_value={'rows':[parse_record({**ROW,'district':'Bengaluru Rural'},'Karnataka','Tomato')],'truncated':False}
        page=self.client.get('/market/')
        self.assertIsNone(page.context['district'])
        self.assertTrue(page.context['expanded_scope'])
        self.assertEqual(page.context['cards'][0]['district_name'],'Bengaluru Rural')
        self.assertContains(page,'Showing reported markets in this state.')
        self.assertEqual(page.context['cards'][0]['modal_price'],Decimal(1000))

    def test_default_district_with_prices_keeps_local_scope(self,mock):
        self.data(mock)
        page=self.client.get('/market/')
        self.assertEqual(page.context['district']['name'],'Bengaluru')
        self.assertFalse(page.context['expanded_scope'])
        self.assertEqual(len(page.context['cards']),1)

    def test_empty_explicit_selection_links_to_reported_markets(self,mock):
        self.data(mock)
        page=self.client.get('/market/',{'state':16,'district':261,'crop':65,'unit':'kg'})
        self.assertEqual(page.context['cards'],[])
        self.assertFalse(page.context['expanded_scope'])
        link=page.context['reported_markets_url']
        self.assertIn('district=&market=',link)
        self.assertIn('unit=kg',link)
        page=self.client.get('/market/'+link)
        self.assertEqual(page.context['cards'][0]['modal_price'],Decimal(10))

    def test_empty_feed_does_not_claim_expanded_prices(self,mock):
        mock.return_value={'rows':[],'truncated':False}
        page=self.client.get('/market/')
        self.assertEqual(page.context['cards'],[])
        self.assertFalse(page.context['expanded_scope'])
        self.assertIsNone(page.context['reported_markets_url'])

    def test_missing_location_never_shows_other_district_prices(self,mock):
        self.data(mock)
        page=self.client.get('/market/',{'state':16,'district':261,'crop':65})
        self.assertEqual(page.context['cards'],[])
        self.assertContains(page,'No prices reported for this selection.')

    def test_invalid_explicit_location_does_not_broaden_search(self,mock):
        self.data(mock)
        page=self.client.get('/market/',{'state':16,'district':'nonexistent','crop':65})
        self.assertEqual(page.context['cards'],[])

    def test_provider_only_district_and_market_are_selectable(self,mock):
        mock.return_value={'rows':[parse_record({**ROW,'district':'New District','market':'New Mandi'},'Karnataka','Tomato')],'truncated':False}
        page=self.client.get('/market/',{'state':16,'district':'New District','market':'New Mandi','crop':65})
        self.assertEqual(len(page.context['cards']),1)
        self.assertEqual(page.context['market']['name'],'New Mandi')

    def test_source_prices_remain_original_when_displaying_kg(self,mock):
        self.data(mock)
        page=self.client.get('/market/',{'unit':'kg'})
        card=page.context['cards'][0]
        self.assertEqual(card['modal_price'],Decimal(10))
        self.assertEqual(card['source_prices']['modal_price'],Decimal(1000))
        self.assertContains(page,'Verify source report')
        self.assertContains(page,'Report date')

    def test_invalid_explicit_crop_never_silently_shows_tomato(self,mock):
        page=self.client.get('/market/',{'crop':'not-a-crop'})
        self.assertEqual(page.context['cards'],[])
        self.assertIsNone(page.context['crop'])
        mock.assert_not_called()

    def test_failure_has_no_placeholder_market_quotes(self,mock):
        mock.side_effect=LocalPriceError('Market prices are unavailable right now. Please try again later.')
        page=self.client.get('/market/')
        self.assertEqual(page.context['cards'],[])
        self.assertContains(page,'Market prices are unavailable right now.')
