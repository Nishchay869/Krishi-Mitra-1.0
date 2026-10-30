import json
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .fertilizer import calculate_plant_fertilizer
from .fertilizer_presets import PRESETS
from .fertilizer_products import PRODUCT_PHOTOS, shop_search_url


class ExpandedPresetTests(SimpleTestCase):
    def test_broad_catalog_has_fruits_and_flowers(self):
        crops={p['crop'] for p in PRESETS.values()}
        self.assertGreaterEqual(len(crops),50)
        self.assertTrue({'Rose','Jasmine','Marigold','Tuberose','Orange','Apple','Guava','Pomegranate','Banana'} <= crops)
        self.assertEqual(len({p['group'] for p in PRESETS.values()}),8)

    def test_per_plant_rate_uses_count_not_assumed_field_density(self):
        first=calculate_plant_fertilizer(nitrogen=12,phosphorus=24,potassium=24,
                                         plant_count=100,area=1,area_unit='ha')
        larger=calculate_plant_fertilizer(nitrogen=12,phosphorus=24,potassium=24,
                                          plant_count=100,area=20,area_unit='ha')
        self.assertEqual(first['products'],larger['products'])
        self.assertEqual(first['plant_count'],100)
        self.assertEqual(larger['area_ha'],20)
        doubled=calculate_plant_fertilizer(nitrogen=12,phosphorus=24,potassium=24,
                                           plant_count=200,area=1,area_unit='ha')
        for a,b in zip(first['products'],doubled['products']):
            self.assertEqual(b['total'],a['total']*2)

    def test_product_photos_are_local_valid_and_attributed(self):
        from PIL import Image
        credits=json.loads((settings.BASE_DIR/'static/images/fertilizers/credits.json').read_text())
        for photo in PRODUCT_PHOTOS.values():
            path=settings.BASE_DIR/'static'/photo['photo']
            self.assertTrue(path.is_file())
            self.assertIn(path.name,credits)
            with Image.open(path) as image:
                image.verify()
            self.assertTrue(photo['photo_source'].startswith('https://'))

    def test_shop_query_is_a_google_maps_search_without_credentials(self):
        url=shop_search_url('Mysuru, Karnataka, India','MOP')
        parsed=urlsplit(url)
        self.assertEqual(parsed.netloc,'www.google.com')
        self.assertEqual(parse_qs(parsed.query),{'api':['1'],'query':['MOP fertilizer shops near Mysuru, Karnataka, India']})


class ExpandedCalculatorPageTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username='expanded-fertilizer')
        profile=self.user.profile
        profile.village='Nanjangud';profile.district='Mysuru';profile.state='Karnataka';profile.save()
        self.client.force_login(self.user)
        self.url=reverse('crops:fertilizer')

    def test_flower_requires_area_and_actual_plant_count(self):
        response=self.client.get(self.url,{'crop_preset':'rose'})
        self.assertContains(response,'name="area"')
        self.assertContains(response,'name="plant_count"')
        self.assertNotContains(response,'name="tree_count"')
        self.assertEqual(response.context['form']['nitrogen'].value(),12)
        response=self.client.post(self.url,{'crop_preset':'rose','planting_type':'plants',
            'nitrogen':12,'phosphorus':24,'potassium':24,'area':1,'area_unit':'ha'})
        self.assertIsNone(response.context['result'])
        self.assertIn('plant_count',response.context['form'].errors)

    def test_flower_application_preserves_area_count_and_schedule(self):
        response=self.client.post(self.url,{'crop_preset':'rose','planting_type':'plants',
            'nitrogen':12,'phosphorus':24,'potassium':24,'area':1,'area_unit':'ha','plant_count':100})
        result=response.context['result']
        self.assertIsNotNone(result)
        detail=self.client.get(result['combinations'][0]['application_url'])
        self.assertEqual(detail.status_code,200)
        self.assertEqual(detail.context['result']['plant_count'],100)
        self.assertEqual(len(detail.context['schedule']['stages']),2)
        back=self.client.get(detail.context['back_url'])
        self.assertEqual(back.context['form']['plant_count'].value(),'100')

    def test_details_show_real_images_and_saved_location_shop_links(self):
        response=self.client.post(self.url,{'crop_preset':'taro','planting_type':'plants',
            'nitrogen':40,'phosphorus':60,'potassium':120,'area':1,'area_unit':'ha'})
        detail=self.client.get(response.context['result']['combinations'][0]['application_url'])
        self.assertContains(detail,'images/fertilizers/tsp.png')
        self.assertContains(detail,'images/fertilizers/mop.png')
        self.assertContains(detail,'images/fertilizers/urea.png')
        self.assertContains(detail,'Nearby fertilizer shops')
        self.assertEqual(detail.context['shop_location'],'Nanjangud, Mysuru, Karnataka, India')
        for product in detail.context['combination']['products']:
            query=parse_qs(urlsplit(product['shop_search_url']).query)['query'][0]
            self.assertIn('Nanjangud, Mysuru, Karnataka, India',query)
            self.assertIn(product['short_name'],query)

    def test_tree_count_does_not_use_field_size(self):
        response=self.client.get(self.url,{'planting_type':'trees','crop_preset':'guava-bearing'})
        self.assertContains(response,'name="tree_count"')
        self.assertNotContains(response,'name="plant_count"')
        self.assertNotContains(response,'name="area"')

    def test_pumpkin_counts_pits_instead_of_guessing_plants_per_pit(self):
        response=self.client.get(self.url,{'crop_preset':'pumpkin'})
        self.assertEqual(response.context['form'].fields['plant_count'].label,'Planting pits in this field')

    def test_shop_location_form_redirects_to_live_maps_without_javascript(self):
        response=self.client.get(reverse('crops:fertilizer_shops'), {'location':'Mandya, Karnataka'})
        self.assertEqual(response.status_code,302)
        query=parse_qs(urlsplit(response.url).query)
        self.assertEqual(query['query'],['fertilizer shops near Mandya, Karnataka'])
        profile=self.user.profile
        profile.refresh_from_db()
        self.assertEqual(profile.district,'Mysuru')

    def test_shop_redirect_cannot_be_used_as_an_open_redirect(self):
        response=self.client.get(reverse('crops:fertilizer_shops'), {'location':'https://example.com/<script>'})
        self.assertEqual(urlsplit(response.url).netloc,'www.google.com')
        self.assertIn('https://example.com/<script>',parse_qs(urlsplit(response.url).query)['query'][0])


class ProductVariantTests(SimpleTestCase):
    def test_multiple_real_brands_for_each_requested_type(self):
        from .fertilizer_products import PRODUCT_VARIANTS
        from PIL import Image
        for code in ('MOP','DAP','UREA'):
            variants=PRODUCT_VARIANTS[code]
            self.assertGreaterEqual(len(variants),2)
            self.assertEqual(len({item['id'] for item in variants}),len(variants))
            for item in variants:
                with Image.open(settings.BASE_DIR/'static'/item['photo']) as image:
                    image.verify()
                self.assertTrue(item['photo_source'].startswith('https://'))

    def test_shop_searches_use_brand_and_fertilizer_type(self):
        from .fertilizer_products import relevant_products
        from .fertilizer import calculate_fertilizer
        result=calculate_fertilizer(nitrogen=150,phosphorus=75,potassium=50,area=1,area_unit='ha')
        cards=relevant_products(result['combinations'][1]['products'],'Mysuru, Karnataka')
        self.assertEqual({c['code'] for c in cards},{'DAP','MOP','UREA'})
        self.assertEqual(len([c for c in cards if c['code']=='DAP']),3)
        self.assertTrue(any('IFFCO' in c['photo_label'] for c in cards))
        self.assertTrue(any('Jai Kisaan' in c['photo_label'] for c in cards))
        for card in cards:
            query=parse_qs(urlsplit(card['shop_search_url']).query)['query'][0]
            self.assertIn(card['shop_query'],query)
            self.assertIn('Mysuru, Karnataka',query)

    def test_variants_do_not_change_the_calculated_nutrient_quantities(self):
        from .fertilizer_products import relevant_products
        from .fertilizer import calculate_fertilizer
        result=calculate_fertilizer(nitrogen=150,phosphorus=75,potassium=50,area=1,area_unit='ha')
        products=result['combinations'][1]['products']
        before=[dict(p) for p in products]
        cards=relevant_products(products,'Mandya')
        self.assertEqual(products,before)
        for card in cards:
            original=next(p for p in products if p['code']==card['code'])
            self.assertEqual(card['grade'],original['grade'])
            self.assertEqual(card['total'],original['total'])
