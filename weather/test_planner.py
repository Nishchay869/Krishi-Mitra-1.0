from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from .planner import build_plan
from .services import summarize

ZONE=timezone(timedelta(hours=5,minutes=30))
START=datetime(2026,10,29,9,0,tzinfo=ZONE)


def forecast(**changes):
    slots=[]
    for index in range(10):
        when=START+timedelta(hours=3*index)
        slots.append({'time':when.isoformat(),'temp':24,'humidity':65,'wind':2,'gust':2.5,
                      'rain':0,'pop':0,'code':800,'daylight':6<=when.hour<18,'description':'clear sky',**changes})
    days=[]
    for key in sorted({s['time'][:10] for s in slots}):
        days.append({'date':key,'slots':[s for s in slots if s['time'][:10]==key],
                     'temp_min':20,'temp_max':26,'rain_mm':0,'humidity':65,'pressure':1010,'wind_speed':2,'description':'clear sky'})
    return days


class PlannerTests(SimpleTestCase):
    def test_good_weather_is_conditional_not_safe(self):
        result=build_plan(forecast(),['Tomato'],soil='dry',now=START)
        self.assertEqual(result['slots'][0]['spray'],'Check conditions')
        self.assertEqual(result['slots'][0]['irrigation'],'Check conditions')
        self.assertEqual(result['crops'][0]['crop'],'Tomato')

    def test_rain_calm_wind_heat_and_missing_data(self):
        for change in ({'rain':1},{'pop':.5},{'wind':0},{'gust':6},{'temp':39},{'daylight':False}):
            result=build_plan(forecast(**change),['Tomato'],now=START)
            self.assertEqual(result['slots'][0]['spray'],'Avoid')
        result=build_plan(forecast(pop=None),['Tomato'],now=START)
        self.assertEqual(result['slots'][0]['spray'],'Insufficient forecast')
        self.assertEqual(result['slots'][-1]['spray'],'Insufficient forecast')

    def test_upcoming_rain_prevents_spray_and_unknown_soil_never_prescribes_water(self):
        days=forecast();days[0]['slots'][2]['pop']=.8
        result=build_plan(days,['Tomato'],now=START)
        self.assertEqual(result['slots'][0]['spray'],'Avoid')
        result=build_plan(forecast(),['Tomato'],now=START)
        self.assertEqual(result['slots'][0]['irrigation'],'Check soil first')
        result=build_plan(forecast(),['Tomato'],soil='wet',now=START)
        self.assertEqual(result['slots'][0]['irrigation'],'Avoid')

    def test_rice_and_pots_are_distinct_and_past_slots_hidden(self):
        result=build_plan(forecast(),['Rice'],soil='dry',now=START)
        self.assertIsNone(result['crops'][0]['water'])
        self.assertEqual(result['slots'][0]['irrigation'],'Check paddy water level.')
        result=build_plan(forecast(),['Tomato'],'pots',now=START+timedelta(hours=2))
        self.assertEqual(result['crops'][0]['note'],'Check pot drainage.')
        self.assertTrue(all(s['when']>=START+timedelta(hours=2) for s in result['slots']))

    def test_missing_interval_never_makes_a_spray_window(self):
        days=forecast();days[0]['slots'].pop(1)
        self.assertEqual(build_plan(days,['Tomato'],now=START)['slots'][0]['spray'],'Insufficient forecast')

    def test_explanation_matches_temperature_and_rain_checks(self):
        result=build_plan(forecast(temp=39),['Tomato'],now=START)
        checks={c['label']:c for c in result['slots'][0]['checks']}
        self.assertFalse(checks['Temperature (°C)']['ok'])
        self.assertTrue(checks['Relative humidity (%)']['ok'])
        self.assertEqual(checks['Temperature (°C)']['value'],'39 °C')
        result=build_plan(forecast(pop=.8),['Tomato'],now=START)
        checks={c['label']:c for c in result['slots'][0]['checks']}
        self.assertEqual(checks['Rain chance']['value'],'80%')
        self.assertFalse(checks['Rain chance']['ok'])
        self.assertEqual(result['slots'][-1]['checks'][0]['value'],'—')

    def test_provider_local_date_is_used(self):
        when=datetime(2026,10,28,21,tzinfo=timezone.utc)
        payload={'city':{'timezone':19800},'list':[{'dt':int(when.timestamp()),'main':{'temp':24,'temp_min':22,'temp_max':25,'humidity':65,'pressure':1010},'wind':{'speed':2},'weather':[{'id':800,'description':'clear sky'}],'pop':0,'sys':{'pod':'n'}}]}
        day=summarize(payload)[0]
        self.assertEqual(day['date'],'2026-10-29')
        self.assertIn('+05:30',day['slots'][0]['time'])


class PlannerViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('planner-farmer');p=self.user.profile
        p.village='Pandavapura';p.district='Mandya';p.state='Karnataka';p.selected_crops=['Tomato','Rice'];p.save();self.client.force_login(self.user)

    @patch('weather.views.fetch_village_forecast',return_value=[])
    def test_saved_signup_crops_are_loaded(self,mock):
        result=self.client.get('/weather/')
        self.assertEqual(result.context['saved_crops'],['Tomato','Rice'])
        mock.assert_called_once_with('Pandavapura','Mandya','Karnataka')
        self.assertContains(result,'Farm activity planner')

    @patch('weather.views.fetch_village_forecast')
    def test_crops_without_a_forecast_never_show_safe_windows(self,mock):
        mock.return_value=[]
        result=self.client.get('/weather/',{'soil':'invalid'})
        self.assertEqual(result.context['soil'],'unknown')
        self.assertEqual(result.context['plan']['slots'],[])
