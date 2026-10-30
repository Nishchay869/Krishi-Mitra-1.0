from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from . import pests


class PestLibraryTests(TestCase):
    def test_saved_crop_order_and_explicit_selection(self):
        user=get_user_model().objects.create_user(username='pest-reader')
        user.profile.selected_crops=['Onion','Tomato'];user.profile.save()
        self.client.force_login(user)
        response=self.client.get(reverse('crops:pests'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['crop']['name'],'Onion')
        self.assertEqual([c['name'] for c in response.context['saved_crops']],['Onion','Tomato'])
        response=self.client.get(reverse('crops:pests'),{'crop':'tomato'})
        self.assertEqual(response.context['crop']['name'],'Tomato')

    def test_guest_default_and_invalid_selection(self):
        response=self.client.get(reverse('crops:pests'))
        self.assertEqual(response.context['crop']['name'],'Tomato')
        self.assertEqual(self.client.get(reverse('crops:pests'),{'crop':'unknown'}).status_code,404)
        self.assertEqual(self.client.get(reverse('crops:pests'),{'stage':'unknown'}).status_code,404)

    def test_stage_search_and_type_filters_combine(self):
        response=self.client.get(reverse('crops:pests'),{'crop':'tomato','stage':'vegetative','type':'pest','q':'whitefl'})
        self.assertEqual(response.status_code,200)
        sections=response.context['sections']
        self.assertEqual(len(sections),1)
        self.assertEqual([r['id'] for r in sections[0]['issues']],['whiteflies'])
        response=self.client.get(reverse('crops:pests'),{'q':'nonexistent-symptom'})
        self.assertContains(response,'No matching entries')

    def test_detail_rejects_issue_from_another_crop(self):
        self.assertEqual(self.client.get(reverse('crops:pest_detail',args=['tomato','late-blight'])).status_code,200)
        self.assertEqual(self.client.get(reverse('crops:pest_detail',args=['tomato','coffee-rust'])).status_code,404)

    def test_catalog_integrity_and_sources(self):
        from .library import catalog
        self.assertEqual({c['name'] for c in pests.crops()},{c['name'] for c in catalog()})
        for crop in pests.crops():
            rows=pests.issues_for(crop)
            self.assertTrue(rows,crop['name'])
            for row in rows:
                self.assertTrue(row['stages'],row['id'])
                self.assertTrue(row['sources'],row['id'])
                self.assertTrue(all(s['url'].startswith('https://') for s in row['sources']))
                if row['photo']:
                    self.assertTrue((Path('static')/row['photo_path']).is_file())
                    for field in ['source','license','artist','sha256']:
                        self.assertTrue(row['photo'][field],(row['id'],field))

    def test_every_displayed_reference_photo_is_verified_for_its_crop(self):
        for crop in pests.crops():
            for issue in pests.issues_for(crop):
                if issue['photo']:
                    self.assertIn(crop['slug'], issue['photo']['verified_crops'],
                                  (crop['name'], issue['id'], issue['photo']['title']))

    def test_tomato_excludes_other_hosts_and_uses_crop_specific_photos(self):
        crops = {c['slug']: c for c in pests.crops()}
        tomato = {r['id']: r for r in pests.issues_for(crops['tomato'])}
        for issue in ['damping-off', 'powdery-mildew', 'fusarium-wilt', 'whiteflies', 'root-knot']:
            self.assertFalse(tomato[issue]['photo_url'], issue)
        for issue in ['bacterial-spot', 'mosaic', 'leaf-curl', 'spider-mites']:
            self.assertTrue(tomato[issue]['photo_url'], issue)
            self.assertEqual(tomato[issue]['photo']['verified_crops'], ['tomato'])
        potato = {r['id']: r for r in pests.issues_for(crops['potato'])}
        self.assertNotEqual(tomato['late-blight']['photo_url'], potato['late-blight']['photo_url'])
        self.assertNotEqual(tomato['early-blight']['photo_url'], potato['early-blight']['photo_url'])

    def test_missing_crop_photograph_is_explicit_in_both_pages(self):
        response = self.client.get(reverse('crops:pests'), {'crop': 'tomato'})
        self.assertContains(response, 'A verified photo for Tomato has not been added yet.')
        self.assertNotContains(response, 'images/pests/damping-off.jpg')
        detail = self.client.get(reverse('crops:pest_detail', args=['tomato','fusarium-wilt']))
        self.assertContains(detail, 'A verified photo for Tomato has not been added yet.')
        self.assertNotContains(detail, 'images/pests/fusarium-wilt.jpg')
