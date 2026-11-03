from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .fertilizer import calculate_fertilizer, calculate_tree_fertilizer
from .forms import FertilizerForm


class FertilizerCalculationTests(SimpleTestCase):
    def calculate(self, **overrides):
        return calculate_fertilizer(**dict(
            dict(nitrogen=120, phosphorus=60, potassium=40, area=2, area_unit='ha'),
            **overrides))

    def test_nutrient_mass_balance_credits_dap_nitrogen(self):
        result = self.calculate()
        dap, urea, mop = [row['per_unit'] for row in result['products']]
        self.assertAlmostEqual(dap * Decimal('.18') + urea * Decimal('.46'), Decimal(120))
        self.assertAlmostEqual(dap * Decimal('.46'), Decimal(60))
        self.assertAlmostEqual(mop * Decimal('.60'), Decimal(40))
        for row in result['products']:
            self.assertEqual(row['total'], row['per_unit'] * 2)

    def test_acres_conversion(self):
        result = self.calculate(area=1, area_unit='acre')
        self.assertEqual(result['area_ha'], Decimal('0.40468564224'))

    def test_excess_nitrogen_is_visible_and_urea_never_negative(self):
        result = self.calculate(nitrogen=0)
        self.assertEqual(result['products'][1]['total'], 0)
        self.assertGreater(result['excess_n_per_unit'], 0)
        self.assertEqual(result['excess_n_total'], result['excess_n_per_unit'] * 2)

    def test_zero_targets_need_no_product(self):
        result = self.calculate(nitrogen=0, phosphorus=0, potassium=0)
        self.assertTrue(all(row['total'] == 0 for row in result['products']))

    def test_invalid_inputs(self):
        for overrides in ({'area': 0}, {'nitrogen': -1}, {'potassium': 'NaN'},
                          {'area': 'Infinity'}, {'area_unit': 'unknown'}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.calculate(**overrides)


class FertilizerPageTests(TestCase):
    def setUp(self):
        self.url = reverse('crops:fertilizer')
        self.user = get_user_model().objects.create_user(username='fertilizer', password='test-pass')

    def test_login_required(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_page_and_calculation(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get(self.url), 'Fertilizer Calculator')
        response = self.client.post(self.url, {'planting_type': 'plants', 'nitrogen': 120, 'phosphorus': 60,
                                              'potassium': 40, 'area': 2, 'area_unit': 'ha'})
        self.assertContains(response, '260.87')
        self.assertContains(response, 'DAP (18–46–0)')
        self.assertIsNotNone(response.context['result'])

    def test_invalid_post_retains_errors_without_result(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'planting_type': 'plants', 'nitrogen': -1})
        self.assertIsNone(response.context['result'])
        self.assertTrue(response.context['form'].errors)

    def test_form_rejects_nonfinite_and_negative_area(self):
        for value in ('NaN', 'Infinity', '-1', '0'):
            form = FertilizerForm({'planting_type': 'plants', 'nitrogen': 0, 'phosphorus': 0, 'potassium': 0,
                                   'area': value, 'area_unit': 'ha'})
            self.assertFalse(form.is_valid())
            self.assertIn('area', form.errors)

    def test_tree_mode_asks_for_count_instead_of_area(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'planting_type': 'trees'})
        self.assertContains(response, 'name="tree_count"')
        self.assertNotContains(response, 'name="area"')
        self.assertContains(response, 'grams/tree')
        response = self.client.post(self.url, {
            'planting_type': 'trees', 'nitrogen': 460, 'phosphorus': 0,
            'potassium': 0, 'tree_count': 10,
        })
        self.assertEqual(response.context['result']['products'][1]['total'], Decimal(10))
        self.assertContains(response, 'kg/tree')

    def test_tree_count_must_be_positive_whole_number(self):
        for count in ('', '0', '-1', '1.5', 'NaN'):
            form = FertilizerForm({'planting_type': 'trees', 'nitrogen': 100,
                                   'phosphorus': 20, 'potassium': 20, 'tree_count': count},
                                  planting_type='trees')
            self.assertFalse(form.is_valid())
            self.assertIn('tree_count', form.errors)

    def test_field_mode_asks_for_size_instead_of_tree_count(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, 'name="area"')
        self.assertNotContains(response, 'name="tree_count"')

    def test_tree_nutrient_accounting(self):
        result = calculate_tree_fertilizer(nitrogen=500, phosphorus=230,
                                           potassium=300, tree_count=7)
        dap, urea, mop = [row['per_unit'] for row in result['products']]
        self.assertEqual(dap, Decimal('.5'))
        self.assertEqual(mop, Decimal('.5'))
        self.assertAlmostEqual(dap * Decimal('.18') + urea * Decimal('.46'), Decimal('.5'))
        self.assertEqual(result['products'][0]['total'], Decimal('3.5'))

    def test_tree_mode_does_not_accept_area_in_place_of_count(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'planting_type': 'trees', 'nitrogen': 100, 'phosphorus': 20,
            'potassium': 20, 'area': 2, 'area_unit': 'ha',
        })
        self.assertIsNone(response.context['result'])
        self.assertIn('tree_count', response.context['form'].errors)

    def test_large_tree_rate_and_zero_targets(self):
        form = FertilizerForm({'planting_type': 'trees', 'nitrogen': 2000,
                               'phosphorus': 0, 'potassium': 0, 'tree_count': 5},
                              planting_type='trees')
        self.assertTrue(form.is_valid(), form.errors)
        result = calculate_tree_fertilizer(nitrogen=0, phosphorus=0, potassium=0, tree_count=5)
        self.assertTrue(all(row['total'] == 0 for row in result['products']))
        for count in (0, -1, '1.5', 'NaN'):
            with self.subTest(count=count), self.assertRaises(ValueError):
                calculate_tree_fertilizer(nitrogen=100, phosphorus=0, potassium=0, tree_count=count)

    def test_crop_selector_prefills_matching_nutrients(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'crop_preset': 'taro'})
        self.assertEqual(response.context['form']['nitrogen'].value(), 40)
        self.assertEqual(response.context['form']['phosphorus'].value(), 60)
        self.assertEqual(response.context['form']['potassium'].value(), 120)
        self.assertContains(response, 'value="taro" selected')
        self.assertContains(response, 'horti_veg_fert_colacasia.html')

    def test_tree_crop_and_age_prefill_and_require_tree_count(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {'planting_type': 'trees', 'crop_preset': 'coconut-5'})
        self.assertEqual(response.context['form']['nitrogen'].value(), 560)
        self.assertEqual(response.context['form']['phosphorus'].value(), 320)
        self.assertEqual(response.context['form']['potassium'].value(), 1200)
        self.assertContains(response, 'name="tree_count"')
        self.assertNotContains(response, 'name="area"')

    def test_saved_crop_is_preselected(self):
        profile = self.user.profile
        profile.selected_crops = ['Onion']
        profile.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context['selected_preset'], 'onion')
        self.assertEqual(response.context['form']['nitrogen'].value(), 60)

    def test_post_preserves_edited_nutrients_and_marks_result(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'planting_type': 'plants', 'crop_preset': 'taro', 'nitrogen': 100,
            'phosphorus': 60, 'potassium': 120, 'area': 1, 'area_unit': 'ha',
        })
        self.assertTrue(response.context['customized'])
        self.assertEqual(response.context['form']['nitrogen'].value(), '100')
        self.assertContains(response, 'Edited nutrient rates')
        self.assertEqual(response.context['selected_preset'], 'taro')

    def test_default_rates_are_not_marked_as_edited(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'planting_type': 'plants', 'crop_preset': 'onion', 'nitrogen': 60,
            'phosphorus': 60, 'potassium': 30, 'area': 40, 'area_unit': 'gunta',
        })
        self.assertFalse(response.context['customized'])
        self.assertEqual(response.context['result']['area_ha'], Decimal('0.404685642240'))

    def test_cross_mode_preset_cannot_be_calculated(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'planting_type': 'plants', 'crop_preset': 'coconut-5', 'nitrogen': 60,
            'phosphorus': 60, 'potassium': 30, 'area': 1, 'area_unit': 'ha',
        })
        self.assertIsNone(response.context['result'])
        self.assertIn('crop_preset', response.context['form'].errors)

    def test_invalid_post_keeps_selected_crop_and_entered_values(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'planting_type': 'plants', 'crop_preset': 'okra', 'nitrogen': 50,
            'phosphorus': 50, 'potassium': 30, 'area': -1, 'area_unit': 'ha',
        })
        self.assertIsNone(response.context['result'])
        self.assertEqual(response.context['selected_preset'], 'okra')
        self.assertEqual(response.context['form']['nitrogen'].value(), '50')

    def test_all_presets_have_sources_units_and_matching_crop_types(self):
        from .fertilizer_presets import PRESETS
        for preset in PRESETS.values():
            self.assertTrue(preset['source'].startswith(('https://agritech.tnau.ac.in/','https://egovernance.vikaspedia.in/')))
            self.assertEqual(len(preset['rates']), 3)
            self.assertTrue(all(0 <= rate <= 10000 for rate in preset['rates']))
            self.assertEqual(preset['mode'] == 'trees', 'age' in preset)


class AdminFertilizerPresetTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(username='admin_agri', password='pass', is_staff=True)
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        self.farmer_user = User.objects.create_user(username='farmer_ramesh', password='pass')
        self.farmer_user.profile.role = 'farmer'
        self.farmer_user.profile.save()

        self.calc_url = reverse('crops:fertilizer')
        self.manage_url = reverse('crops:fertilizer_manage')
        self.save_url = reverse('crops:fertilizer_preset_save')

    def test_admin_manage_page_access_restricted_to_admins(self):
        # Non-logged in redirects to login
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 302)

        # Farmer user gets redirected
        self.client.force_login(self.farmer_user)
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 302)

        # Admin user gets 200
        self.client.force_login(self.admin_user)
        response = self.client.get(self.manage_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standard Fertilizer N-P-K Presets')
        self.assertContains(response, 'Tomato')

    def test_admin_can_update_preset_and_reflects_to_all_users(self):
        from .models import FertilizerPreset
        from .fertilizer_presets import get_effective_presets

        # 1. Admin saves new N, P, K values for tomato (default was 150, 100, 50)
        self.client.force_login(self.admin_user)
        response = self.client.post(self.calc_url, {
            'save_as_admin_default': '1',
            'crop_preset': 'tomato',
            'planting_type': 'plants',
            'nitrogen': '180',
            'phosphorus': '110',
            'potassium': '65',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standard N-P-K rates for Tomato updated')

        # Check DB model
        preset_row = FertilizerPreset.objects.get(preset_key='tomato')
        self.assertEqual(float(preset_row.nitrogen), 180.0)
        self.assertEqual(float(preset_row.phosphorus), 110.0)
        self.assertEqual(float(preset_row.potassium), 65.0)
        self.assertEqual(preset_row.updated_by, self.admin_user)

        # 2. Log in as a normal farmer and check that tomato's new rates reflect immediately
        self.client.force_login(self.farmer_user)
        response = self.client.get(self.calc_url, {'crop_preset': 'tomato', 'planting_type': 'plants'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.context['form']['nitrogen'].value()), 180.0)
        self.assertEqual(float(response.context['form']['phosphorus'].value()), 110.0)
        self.assertEqual(float(response.context['form']['potassium'].value()), 65.0)
        self.assertEqual(response.context['preset']['rates'], (180.0, 110.0, 65.0))
        self.assertContains(response, '180')
        self.assertContains(response, '110')
        self.assertContains(response, '65')

    def test_admin_update_via_manage_endpoint(self):
        from .models import FertilizerPreset

        self.client.force_login(self.admin_user)
        response = self.client.post(self.save_url, {
            'preset_key': 'wheat',
            'nitrogen': '95.5',
            'phosphorus': '45',
            'potassium': '42.5',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standard N-P-K rates for Wheat saved successfully')

        preset_row = FertilizerPreset.objects.get(preset_key='wheat')
        self.assertEqual(float(preset_row.nitrogen), 95.5)
        self.assertEqual(float(preset_row.phosphorus), 45.0)
        self.assertEqual(float(preset_row.potassium), 42.5)

        # Farmer verifies wheat rates
        self.client.force_login(self.farmer_user)
        response = self.client.get(self.calc_url, {'crop_preset': 'wheat', 'planting_type': 'plants'})
        self.assertEqual(response.context['preset']['rates'], (95.5, 45.0, 42.5))

    def test_admin_update_via_ajax(self):
        from .models import FertilizerPreset

        self.client.force_login(self.admin_user)
        response = self.client.post(
            self.save_url,
            {'preset_key': 'rice', 'nitrogen': '165', 'phosphorus': '55', 'potassium': '52'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['rates'], [165.0, 55.0, 52.0])

        preset_row = FertilizerPreset.objects.get(preset_key='rice')
        self.assertEqual(float(preset_row.nitrogen), 165.0)

    def test_farmer_cannot_save_as_admin_default(self):

        from .fertilizer_presets import get_effective_presets
        initial_rates = get_effective_presets()['potato']['rates']

        # Normal farmer attempts to post save_as_admin_default
        self.client.force_login(self.farmer_user)
        response = self.client.post(self.calc_url, {
            'save_as_admin_default': '1',
            'crop_preset': 'potato',
            'nitrogen': '999',
            'phosphorus': '999',
            'potassium': '999',
        }, follow=True)
        self.assertContains(response, 'Only administrators can update standard N-P-K preset rates')

        # Potato rates must not have changed
        current_rates = get_effective_presets()['potato']['rates']
        self.assertEqual(current_rates, initial_rates)

