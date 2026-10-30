from decimal import Decimal
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .fertilizer import PRODUCTS, calculate_fertilizer, calculate_tree_fertilizer, calculate_plant_fertilizer
from .fertilizer_application import STAGES, application_stages
from .fertilizer_presets import PRESETS
from .views import FERTILIZER_TOKEN_SALT


class CombinationMathTests(SimpleTestCase):
    def test_both_combinations_supply_requested_nutrients(self):
        result = calculate_fertilizer(nitrogen=150, phosphorus=75, potassium=50,
                                      area=1, area_unit='ha')
        for combo in result['combinations']:
            masses = {p['code']: p['total'] for p in combo['products']}
            n = masses['UREA'] * Decimal('.46') + masses.get('DAP', 0) * Decimal('.18')
            p = (masses.get('DAP', 0) + masses.get('TSP', 0)) * Decimal('.46')
            k = masses['MOP'] * Decimal('.60')
            self.assertAlmostEqual(n, Decimal(150))
            self.assertAlmostEqual(p, Decimal(75))
            self.assertAlmostEqual(k, Decimal(50))
            for product in combo['products']:
                self.assertEqual(product['bags'], product['total'] / PRODUCTS[product['code']]['bag_kg'])

    def test_tsp_option_avoids_excess_nitrogen(self):
        result = calculate_fertilizer(nitrogen=0, phosphorus=60, potassium=0,
                                      area=1, area_unit='ha')
        tsp, dap = result['combinations']
        self.assertEqual(tsp['excess_n_total'], 0)
        self.assertGreater(dap['excess_n_total'], 0)

    def test_stage_masses_sum_to_combination_total_for_every_preset(self):
        for key, preset in PRESETS.items():
            inputs = dict(zip(('nitrogen','phosphorus','potassium'), map(Decimal, preset['rates'])))
            if preset['mode'] == 'trees':
                inputs['tree_count'] = 7
                result = calculate_tree_fertilizer(**inputs)
            else:
                inputs.update(area=Decimal('2.4'), area_unit='acre')
                if preset.get('basis') == 'plant':
                    inputs['plant_count'] = 37
                    result = calculate_plant_fertilizer(**inputs)
                else:
                    result = calculate_fertilizer(**inputs)
            for combo in result['combinations']:
                with self.subTest(preset=key, combination=combo['id']):
                    plan = application_stages(key, preset, inputs, result, combo['id'])
                    if key == 'cucumber' and combo['id'] == 'dap':
                        self.assertFalse(plan['stages'])
                        self.assertIn('early stage', plan['unavailable'])
                        continue
                    if plan['unavailable']:
                        self.assertFalse(plan['stages'])
                        self.assertTrue('not available' in plan['unavailable'] or 'early stage' in plan['unavailable'] or 'exceeds' in plan['unavailable'])
                        continue
                    self.assertTrue(plan['stages'], plan['unavailable'])
                    for product in combo['products']:
                        total = sum(p['total'] for s in plan['stages'] for p in s['products']
                                    if p['code'] == product['code'])
                        self.assertAlmostEqual(total, product['total'])

    def test_edited_rates_do_not_receive_an_unverified_schedule(self):
        result=calculate_fertilizer(nitrogen=150,phosphorus=75,potassium=50,area=1,area_unit='ha')
        plan=application_stages('cucumber',PRESETS['cucumber'],{},result,'tsp',customized=True)
        self.assertFalse(plan['stages'])
        self.assertIn('Edited',plan['unavailable'])

    def test_source_fraction_totals(self):
        from fractions import Fraction
        for key, stages in STAGES.items():
            for nutrient in range(3):
                self.assertEqual(sum(Fraction(ratios[nutrient]) for _,ratios in stages), 1, key)


class ApplicationPageTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='application-user')
        self.client.force_login(self.user)
        self.data={'planting_type':'plants','crop_preset':'taro','nitrogen':40,
                   'phosphorus':60,'potassium':120,'area':2,'area_unit':'ha'}
        self.calculator=reverse('crops:fertilizer')

    def result_links(self, data=None):
        response=self.client.post(self.calculator,data or self.data)
        self.assertEqual(response.status_code,200)
        return {c['id']: c['application_url'] for c in response.context['result']['combinations']}

    def test_combination_cards_and_details_preserve_area_and_crop(self):
        links=self.result_links()
        self.assertEqual(set(links),{'tsp','dap'})
        for key,url in links.items():
            response=self.client.get(url)
            self.assertEqual(response.status_code,200)
            self.assertContains(response,'Application instructions')
            self.assertContains(response,'45 days after planting')
            self.assertContains(response,'Relevant products')
            self.assertEqual(response.context['result']['area_ha'],2)
            self.assertEqual(response.context['selected_preset'],'taro')
            restored=self.client.get(response.context['back_url'])
            self.assertIsNotNone(restored.context['result'])
            self.assertEqual(restored.context['form']['area'].value(),'2')

    def test_cucumber_tsp_has_source_stage_equivalents_and_drip_notice(self):
        links=self.result_links(dict(self.data,crop_preset='cucumber',nitrogen=150,phosphorus=75,potassium=75))
        response=self.client.get(links['tsp'])
        self.assertEqual(len(response.context['schedule']['stages']),5)
        self.assertContains(response,'not a drip-injection recipe')
        self.assertContains(response,'Crop establishment (days 1–10)')
        response=self.client.get(links['dap'])
        self.assertFalse(response.context['schedule']['stages'])
        self.assertContains(response,'early stage')

    def test_tree_details_use_count_and_annual_schedule(self):
        links=self.result_links({'planting_type':'trees','crop_preset':'coconut-5',
            'nitrogen':560,'phosphorus':320,'potassium':1200,'tree_count':10})
        response=self.client.get(links['tsp'])
        self.assertEqual(response.context['result']['tree_count'],10)
        self.assertContains(response,'June–July')
        self.assertContains(response,'December–January')

    def test_edited_values_survive_details_and_back(self):
        links=self.result_links(dict(self.data,nitrogen=50))
        response=self.client.get(links['tsp'])
        self.assertTrue(response.context['customized'])
        self.assertFalse(response.context['schedule']['stages'])
        restored=self.client.get(response.context['back_url'])
        self.assertEqual(restored.context['form']['nitrogen'].value(),'50')

    def test_missing_tampered_or_wrong_user_calculations_return_404(self):
        url=self.result_links()['tsp']
        self.assertEqual(self.client.get(url+'x').status_code,404)
        self.assertEqual(self.client.get(reverse('crops:fertilizer_application',args=['tsp'])).status_code,404)
        other=get_user_model().objects.create_user(username='other-application-user')
        self.client.force_login(other)
        self.assertEqual(self.client.get(url).status_code,404)

    def test_expired_token_is_rejected(self):
        with patch('django.core.signing.time.time',return_value=1):
            token=signing.dumps({'user':self.user.pk,'inputs':self.data},salt=FERTILIZER_TOKEN_SALT)
        response=self.client.get(reverse('crops:fertilizer_application',args=['tsp']),{'calculation':token})
        self.assertEqual(response.status_code,404)

    def test_unknown_combination_and_anonymous_access(self):
        url=self.result_links()['tsp'].replace('/tsp/','/unknown/')
        self.assertEqual(self.client.get(url).status_code,404)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code,302)
