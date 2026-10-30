from pathlib import Path
import json
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override

from accounts.onboarding import CROP_CHOICES
from .library import catalog


class CropLibraryTests(TestCase):
    def test_all_registered_crops_have_local_photos_and_complete_profiles(self):
        items = catalog()
        self.assertEqual({c['name'] for c in items}, {name for name, _ in CROP_CHOICES})
        self.assertEqual(len({c['slug'] for c in items}), len(items))
        for crop in items:
            self.assertTrue((Path(settings.BASE_DIR) / 'static' / crop['photo']).is_file())
            for key in ('climate', 'sun', 'watering', 'planting', 'soil', 'drainage', 'sources'):
                self.assertTrue(crop[key], (crop['name'], key))
            for name in crop['companions']:
                self.assertIn(name, {c['name'] for c in items})
                self.assertNotEqual(name, crop['name'])

    @patch('requests.sessions.Session.request', side_effect=AssertionError('Library must not use APIs'))
    def test_browse_all_detail_pages_without_external_calls(self, _):
        response = self.client.get(reverse('crops:library'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['count'], 70)
        for crop in catalog():
            response = self.client.get(reverse('crops:library_detail', args=[crop['slug']]))
            self.assertEqual(response.status_code, 200, crop['name'])
            self.assertContains(response, 'library-conditions')
            self.assertNotContains(response, 'Not specified by source')
            self.assertNotContains(response, 'No verified companion listed.')

    def test_search_and_category_are_combined(self):
        response = self.client.get(reverse('crops:library'), {'category':'fruits','q':'mango'})
        self.assertEqual(response.context['count'], 1)
        response = self.client.get(reverse('crops:library'), {'category':'flowers','q':'mango'})
        self.assertEqual(response.context['count'], 0)
        self.assertContains(response, 'No crops found.')

    def test_localized_search(self):
        with override('kn'):
            from django.utils.translation import gettext
            name = gettext('Tomato')
        response = self.client.get(reverse('crops:library'), {'q':name}, HTTP_COOKIE='django_language=kn')
        self.assertEqual(response.context['count'], 1)

    def test_unknown_crop_returns_404(self):
        self.assertEqual(self.client.get('/crops/library/not-a-crop/').status_code, 404)

    def test_companions_link_to_details_and_aquatic_layout_is_explained(self):
        response = self.client.get('/crops/library/coffee/')
        self.assertContains(response, reverse('crops:library_detail', args=['black-pepper']))
        response = self.client.get('/crops/library/lotus/')
        self.assertContains(response, 'Use a separate pond container')
        self.assertContains(response, 'Planting layout')
        self.assertContains(response, 'Standing water')

    def test_researched_content_has_field_sources_and_no_empty_conditions(self):
        for crop in catalog():
            for field in ('temperature', 'humidity', 'ph', 'companion_note'):
                self.assertTrue(crop[field], (crop['name'], field))
            self.assertTrue(crop['rainfall'] or crop['rainfall_note'], crop['name'])
            for field in ('temperature', 'humidity', 'ph', 'companions'):
                self.assertTrue(crop['field_sources'][field]['url'].startswith('https://'))
            self.assertTrue(crop['companions'] or crop['companion_kind'] == 'layout')

    def test_species_ranges_match_research_snapshot(self):
        references = json.loads((Path(settings.BASE_DIR) / 'crops/data/library_references.json').read_text())['species']
        for crop in catalog():
            profiles = crop.get('variants', [dict(crop, taxon=crop['scientific_name'])])
            for profile in profiles:
                evidence = references.get(profile['taxon'])
                if not evidence:
                    continue
                for field in ('temperature', 'rainfall', 'ph'):
                    # Aquatic water management deliberately replaces rainfall targets.
                    if field == 'rainfall' and not profile.get(field):
                        continue
                    expected = evidence['fields'][field]['optimal']
                    actual = [float(v) for v in profile[field].replace(' °C', '').split('–')]
                    self.assertEqual(actual, expected, (crop['name'], field))

    def test_rotations_are_not_presented_as_simultaneous_companions(self):
        response = self.client.get('/crops/library/rice/')
        self.assertContains(response, 'Grow these crops in sequence after harvest')
        self.assertContains(response, '<h2>Crop rotation</h2>', html=True)
        response = self.client.get('/crops/library/grapes/')
        self.assertContains(response, 'Habitat strip')
        self.assertContains(response, 'not a crop-specific pest-control guarantee')

    def test_combined_crop_types_keep_separate_ranges(self):
        for slug, taxa in [('coffee', ('Coffea arabica', 'Coffea canephora')),
                           ('rapeseed-mustard', ('Brassica juncea', 'Brassica napus'))]:
            response = self.client.get(f'/crops/library/{slug}/')
            for taxon in taxa:
                self.assertContains(response, taxon)

    def test_new_guidance_is_bundled_in_every_available_language(self):
        from accounts.languages import available_languages
        for code, _ in available_languages():
            messages = json.loads((Path(settings.BASE_DIR) / f'locale/ui/{code}.json').read_text())
            for crop in catalog():
                for key in ('humidity', 'rainfall_note', 'companion_note'):
                    value = crop.get(key)
                    if value and not any(c.isdigit() for c in value):
                        self.assertIn(value, messages, (code, crop['name'], key))
