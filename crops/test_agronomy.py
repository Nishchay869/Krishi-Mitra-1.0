from django.test import TestCase, Client
from django.urls import reverse
import json

from crops.agronomy import (
    calculate_precision_agronomy,
    calculate_seed_requirement,
    calculate_crop_yield_and_net_margin,
)


class AgronomyEngineTests(TestCase):
    def test_seed_requirement_calculation_formula(self):
        # 1 Acre, 24" row spacing, 8" plant spacing, 90% germ, 98% purity, 40g / 1000 seeds
        res = calculate_seed_requirement(
            area_acres=1.0,
            row_spacing_inches=24.0,
            plant_spacing_inches=8.0,
            germination_rate=0.9,
            purity_rate=0.98,
            seed_weight_grams_per_thousand=40.0,
        )
        # Expected:
        # areaSquareInches = 1 * 43560 * 144 = 6,272,640
        # spacePerPlant = 24 * 8 = 192
        # targetPlantCount = 6,272,640 / 192 = 32,670
        # seedsNeeded = 32,670 / (0.9 * 0.98) = 37,040.816 -> 37,041
        # totalWeightKg = (37,040.816 * 40) / 1,000,000 = 1.4816 -> 1.48 kg
        self.assertEqual(res['totalPlants'], 32670)
        self.assertEqual(res['totalSeeds'], 37041)
        self.assertEqual(res['totalWeightKg'], 1.48)

    def test_crop_yield_and_net_margin_calculation(self):
        # 2 Acres Maize: 28 Qtl/ac @ ₹2,225/Qtl, cost ₹18,000/ac
        res = calculate_crop_yield_and_net_margin(
            crop_name='Maize',
            area_acres=2.0,
            expected_yield_per_acre_qtl=28.0,
            selling_price_per_qtl=2225.0,
            cost_of_cultivation_per_acre=18000.0,
        )
        self.assertEqual(res['total_production_quintals'], 56.0)
        self.assertEqual(res['gross_revenue'], 56.0 * 2225.0)  # ₹124,600
        self.assertEqual(res['total_cost'], 36000.0)
        self.assertEqual(res['net_margin'], 124600.0 - 36000.0)  # ₹88,600 profit
        self.assertEqual(res['net_margin_per_acre'], 44300.0)
        self.assertTrue(res['roi_percent'] > 0)
        self.assertTrue(res['benefit_cost_ratio'] > 1.0)

    def test_rule_a_low_weed_pressure(self):
        result = calculate_precision_agronomy(
            crop_name='Maize',
            field_size=1.0,
            field_unit='Acre',
            season='Kharif',
            soil_type='Loamy',
            irrigation_status='Drip',
            weed_pressure='Low (<15%)',
            weed_types_present=['Broadleaf'],
        )
        self.assertEqual(result.crop_name, 'Maize')
        self.assertEqual(result.buffer_percent, 8.0)
        self.assertIn('5 cm away', result.application_method_details)
        self.assertFalse(result.is_summer)

    def test_rule_a_moderate_weed_pressure(self):
        result = calculate_precision_agronomy(
            crop_name='Tomato',
            field_size=2.0,
            field_unit='Acre',
            season='Rabi',
            soil_type='Sandy',
            irrigation_status='Drip',
            weed_pressure='Moderate (15–35%)',
            weed_types_present=['Grasses'],
        )
        self.assertEqual(result.buffer_percent, 20.0)
        self.assertEqual(result.basal_split_pct, 30)
        self.assertEqual(result.topdress_1_split_pct, 35)
        self.assertIn('20–30%', result.application_method_details)
        self.assertIn('DO NOT dump all excess fertilizer at once', result.application_method_details)

    def test_rule_a_severe_weed_pressure(self):
        result = calculate_precision_agronomy(
            crop_name='Cotton',
            field_size=1.0,
            field_unit='Hectare',
            season='Kharif',
            soil_type='Black Cotton',
            irrigation_status='Rainfed',
            weed_pressure='Severe (>35%)',
            weed_types_present=['Grasses'],
        )
        self.assertEqual(result.buffer_percent, 25.0)
        self.assertEqual(result.weed_loss_risk_pct, 40.0)
        self.assertIn('Critical Period of Weed Control', result.application_method_details)
        self.assertIn('24–48 hours AFTER', result.application_method_details)

    def test_rule_b_summer_season_strategy(self):
        result = calculate_precision_agronomy(
            crop_name='Groundnut',
            field_size=2.5,
            field_unit='Acre',
            season='Summer',
            soil_type='Loamy',
            irrigation_status='Drip',
            weed_pressure='Moderate (15–35%)',
            weed_types_present=['Broadleaf', 'Parthenium hysterophorus', 'Cyperus rotundus'],
        )
        self.assertTrue(result.is_summer)
        self.assertIsNotNone(result.summer_strategy)
        self.assertIn('NEVER recommend 100% clean-weeding', result.summer_strategy['warning'])
        self.assertIn('Root Zone (0–15 cm)', result.summer_strategy['root_zone_strategy'])
        self.assertIn('Inter-Row (>15 cm)', result.summer_strategy['inter_row_strategy'])
        self.assertTrue(any('4–8°C' in b for b in result.summer_strategy['quantified_benefits']))
        self.assertTrue(any('35%' in b for b in result.summer_strategy['quantified_benefits']))

        # Invasive weeds must be flagged
        self.assertIn('Parthenium hysterophorus', result.invasive_weeds_detected)
        self.assertIn('Cyperus rotundus', result.invasive_weeds_detected)
        self.assertIn('Parthenium hysterophorus', result.weeds_to_remove)
        self.assertIn('Cyperus rotundus', result.weeds_to_remove)

    def test_gunta_unit_conversion(self):
        # 40 Guntas = 1 Acre
        result = calculate_precision_agronomy(
            crop_name='Wheat',
            field_size=40.0,
            field_unit='Gunta',
            season='Rabi',
            soil_type='Clay',
            irrigation_status='Flood irrigated',
            weed_pressure='None (0%)',
        )
        self.assertAlmostEqual(result.acres, 1.0, places=2)
        self.assertAlmostEqual(result.guntas, 40.0, places=1)

    def test_expanded_target_crops_resolution(self):
        # Test targeted pulses, millets, oilseeds, spices, vegetables
        test_crops = [
            ('Bajra', 'Bajra'),
            ('pearl millet', 'Bajra'),
            ('Pigeonpea', 'Pigeonpea'),
            ('tur', 'Pigeonpea'),
            ('arhar', 'Pigeonpea'),
            ('Green Gram', 'Green Gram'),
            ('moong', 'Green Gram'),
            ('Sunflower', 'Sunflower'),
            ('surajmukhi', 'Sunflower'),
            ('Watermelon', 'Watermelon'),
            ('tarbooz', 'Watermelon'),
            ('Capsicum', 'Capsicum'),
            ('shimla mirch', 'Capsicum'),
            ('Banana', 'Banana'),
            ('kela', 'Banana'),
        ]
        for query_name, expected_target in test_crops:
            res = calculate_precision_agronomy(
                crop_name=query_name,
                field_size=1.0,
                field_unit='Acre',
                season='Kharif',
                soil_type='Loamy',
                irrigation_status='Drip',
                weed_pressure='Low (<15%)',
            )
            self.assertEqual(res.crop_name, expected_target, f"Failed for {query_name}")
            self.assertTrue(res.baseline_n_kg > 0)
            self.assertIsNotNone(res.seed_requirement)
            self.assertIsNotNone(res.crop_yield_and_net_margin)


class AgronomyApiEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_agronomy_api_returns_structured_assessment(self):
        payload = {
            'crop_name': 'Maize',
            'field_size': 2.0,
            'field_unit': 'Acre',
            'season': 'Summer',
            'soil_type': 'Loamy',
            'irrigation_status': 'Drip',
            'weed_pressure': 'Moderate (15–35%)',
            'weed_types_present': ['Grasses', 'Parthenium hysterophorus'],
        }
        resp = self.client.post(
            reverse('crops:agronomy_api'),
            json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['crop_name'], 'Maize')
        self.assertIn('quantitative_adjustments', data)
        self.assertIn('season_microclimate_management', data)
        self.assertIn('high_yield_action_plan', data)
        self.assertIn('operational_reminder', data)
        self.assertIn('seed_requirement', data)
        self.assertIn('totalPlants', data['seed_requirement'])
        self.assertIn('totalSeeds', data['seed_requirement'])
        self.assertIn('totalWeightKg', data['seed_requirement'])
        self.assertIn('crop_yield_and_net_margin', data)
        self.assertIn('gross_revenue', data['crop_yield_and_net_margin'])
        self.assertIn('net_margin', data['crop_yield_and_net_margin'])
        self.assertTrue(data['season_microclimate_management']['is_summer'])
        self.assertIn('Parthenium hysterophorus', data['season_microclimate_management']['invasive_weeds_detected'])

    def test_yield_api_dispatches_to_agronomy_when_agronomy_params_present(self):
        payload = {
            'crop_name': 'Cotton',
            'field_size': 1.5,
            'field_unit': 'Acre',
            'season': 'Summer',
            'weed_pressure': 'Severe (>35%)',
        }
        resp = self.client.post(
            reverse('crops:yield_api'),
            json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['crop_name'], 'Cotton')
        self.assertEqual(data['quantitative_adjustments']['buffer_percent'], 25.0)

