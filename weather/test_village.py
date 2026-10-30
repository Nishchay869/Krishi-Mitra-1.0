from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings

from .services import FORECAST_URL, GEOCODING_URL, WeatherError, fetch_village_forecast, village_coordinates


def place(name='Pandavapura', state='Karnataka', latitude=12.5, longitude=76.67, **extra):
    return dict(name=name,state=state,country='IN',lat=latitude,lon=longitude,**extra)


def response(payload, status=200):
    return Mock(status_code=status, json=Mock(return_value=payload))


@override_settings(OPENWEATHER_API_KEY='test-key')
class VillageForecastServiceTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch('weather.services.requests.get')
    def test_village_coordinates_are_used_in_the_forecast_request(self, get):
        get.side_effect=[response([place(),place(state='Maharashtra',latitude=18.1)]),
                         response({'city':{'name':'Nearest provider town','timezone':19800},'list':[]})]
        self.assertEqual(fetch_village_forecast('Pandavapura','Mandya','Karnataka'),[])
        geo=get.call_args_list[0]
        self.assertEqual(geo.args[0],GEOCODING_URL)
        self.assertEqual(geo.kwargs['params']['q'],'Pandavapura,IN')
        forecast=get.call_args_list[1]
        self.assertEqual(forecast.args[0],FORECAST_URL)
        self.assertEqual(forecast.kwargs['params']['lat'],12.5)
        self.assertEqual(forecast.kwargs['params']['lon'],76.67)
        self.assertNotIn('q',forecast.kwargs['params'])

    @patch('weather.services.requests.get')
    def test_missing_or_ambiguous_village_never_fetches_district_weather(self,get):
        for payload in ([],[place(name='Mandya')],[place(),place(latitude=12.8)],
                        [place(state='Maharashtra')],[dict(place(),country='US')]):
            cache.clear();get.reset_mock();get.return_value=response(payload)
            with self.subTest(payload=payload),self.assertRaises(WeatherError):
                fetch_village_forecast('Pandavapura','Mandya','Karnataka')
            self.assertEqual(get.call_count,1)
            self.assertEqual(get.call_args.args[0],GEOCODING_URL)

    @patch('weather.services.requests.get')
    def test_local_name_and_state_aliases(self,get):
        get.return_value=response([place(name='Other spelling',state='Orissa',local_names={'or':'ଗାଁ'})])
        self.assertEqual(village_coordinates('ଗାଁ','District','Odisha'),(12.5,76.67))

    @patch('weather.services.requests.get')
    def test_duplicate_provider_records_at_same_point_are_not_ambiguous(self,get):
        get.return_value=response([place(),place()])
        self.assertEqual(village_coordinates('Pandavapura','Mandya','Karnataka'),(12.5,76.67))

    @patch('weather.services.requests.get')
    def test_village_and_point_forecasts_are_cached(self,get):
        get.side_effect=[response([place()]),response({'list':[]})]
        for _ in range(2):
            self.assertEqual(fetch_village_forecast('Pandavapura','Mandya','Karnataka'),[])
        self.assertEqual(get.call_count,2)

    @patch('weather.services.requests.get')
    def test_bad_payloads_and_nonfinite_coordinates_are_rejected(self,get):
        for payload in ({'error':'bad'},[place(latitude='NaN')],[place(longitude=999)],
                        [None],[place(latitude=None)]):
            cache.clear();get.return_value=response(payload)
            with self.subTest(payload=payload),self.assertRaises(WeatherError):
                village_coordinates('Pandavapura','Mandya','Karnataka')

    @patch('weather.services.requests.get',side_effect=requests.Timeout)
    def test_timeout_is_reported_without_another_location_lookup(self,get):
        with self.assertRaises(WeatherError):
            fetch_village_forecast('Pandavapura','Mandya','Karnataka')
        self.assertEqual(get.call_count,1)

    @patch('weather.services.requests.get')
    def test_native_village_names_keep_distinct_vowels(self,get):
        get.return_value=response([place(name='रामपुर')])
        with self.assertRaises(WeatherError):
            village_coordinates('रामपूर','Mandya','Karnataka')

    @override_settings(OPENWEATHER_API_KEY='')
    @patch('weather.services.requests.get')
    def test_missing_api_key_never_makes_an_external_request(self,get):
        with self.assertRaises(WeatherError):
            fetch_village_forecast('Pandavapura','Mandya','Karnataka')
        get.assert_not_called()

    @patch('weather.services.requests.get')
    def test_nearby_boundary_and_locality_records_form_one_village_area(self,get):
        get.return_value=response([place(latitude=13.13986145,longitude=77.62305117),
                                   place(latitude=13.1440103,longitude=77.6191241)])
        lat,lon=village_coordinates('Pandavapura','Mandya','Karnataka')
        self.assertAlmostEqual(lat,13.141935875)
        self.assertAlmostEqual(lon,77.621087635)

    @patch('weather.services.requests.get')
    def test_saved_spelling_variant_uses_verified_village_name(self,get):
        get.return_value=response([place(name='Hunasamaranahalli',latitude=13.1440103,longitude=77.6191241)])
        result=village_coordinates('hunasamaranalli','Bengaluru South','Karnataka')
        self.assertEqual(get.call_args.kwargs['params']['q'],'Hunasamaranahalli,IN')
        self.assertEqual(result,(13.1440103,77.6191241))


class VillagePlannerPageTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='village-planner')
        profile=self.user.profile
        profile.village='Pandavapura';profile.district='Mandya';profile.state='Karnataka'
        profile.save();self.client.force_login(self.user)

    @patch('weather.views.fetch_forecast')
    @patch('weather.views.fetch_village_forecast',return_value=[])
    def test_defaults_to_saved_village_not_district(self,village,legacy):
        result=self.client.get('/weather/')
        village.assert_called_once_with('Pandavapura','Mandya','Karnataka')
        legacy.assert_not_called()
        self.assertEqual(result.context['location'],'Pandavapura, Mandya, Karnataka')
        self.assertContains(result,'Village / town')
        self.assertEqual(self.user.profile.location_query,'Pandavapura')

    @patch('weather.views.fetch_village_forecast',return_value=[])
    def test_submitting_prefilled_location_keeps_village_resolution(self,village):
        self.client.get('/weather/',{'location':'Pandavapura, Mandya, Karnataka','soil':'wet'})
        village.assert_called_once_with('Pandavapura','Mandya','Karnataka')

    @patch('weather.views.fetch_village_forecast',return_value=[])
    def test_manual_village_district_state_override(self,village):
        self.client.get('/weather/',{'location':'Hulikere, Mysuru, Karnataka'})
        village.assert_called_once_with('Hulikere','Mysuru','Karnataka')

    @patch('weather.views.fetch_forecast',return_value=[])
    @patch('weather.views.fetch_village_forecast')
    def test_manual_town_override_is_preserved(self,village,legacy):
        result=self.client.get('/weather/',{'location':'Mysuru'})
        legacy.assert_called_once_with('Mysuru')
        village.assert_not_called()
        self.assertEqual(result.context['location'],'Mysuru')

    @patch('weather.views.fetch_forecast')
    @patch('weather.views.fetch_village_forecast')
    def test_missing_village_asks_for_profile_update_instead_of_auto_using_district(self,village,legacy):
        profile=self.user.profile;profile.village='';profile.save()
        result=self.client.get('/weather/')
        village.assert_not_called();legacy.assert_not_called()
        self.assertEqual(result.context['location'],'')
        self.assertContains(result,'add your village to your profile')

    @patch('weather.views.fetch_forecast')
    @patch('weather.views.fetch_village_forecast',side_effect=WeatherError('Not found'))
    def test_failure_does_not_fall_back_to_district_or_relabel_a_district_forecast(self,village,legacy):
        result=self.client.get('/weather/')
        self.assertEqual(result.status_code,200)
        self.assertTrue(result.context['error'])
        self.assertEqual(result.context['days'],[])
        legacy.assert_not_called()
