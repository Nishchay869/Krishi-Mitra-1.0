import base64
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import PestEntry

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGMUSdFgYGBgYgADAAeWAKQ68ekwAAAAAElFTkSuQmCC')


class PestAdminTests(TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.folder)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(shutil.rmtree, self.folder)
        self.admin = get_user_model().objects.create_user(username='crop-editor', is_staff=True)
        self.url = reverse('crops:pest_edit', args=['tomato', 'late-blight'])
        self.data = {'crop_slug': 'tomato', 'title': 'Late blight edited', 'kind': 'Oomycete',
            'stages': ['vegetative', 'fruiting'], 'symptoms': 'Administrator symptom details',
            'more_info': 'Detailed crop information', 'treat_now': 'Immediate action details',
            'organic_control': 'Organic control details', 'chemical_control': 'Chemical control details',
            'preventive_measures': 'Preventive measure details', 'photo_caption': 'My field photograph'}

    def test_only_admins_can_read_or_write_portal(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)
        farmer = get_user_model().objects.create_user(username='regular-farmer')
        self.client.force_login(farmer)
        for url in [reverse('crops:pest_admin'), reverse('crops:pest_new'), self.url]:
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, self.data).status_code, 403)
        self.assertFalse(PestEntry.objects.exists())

    def test_save_upload_publishes_all_fields_only_for_selected_crop(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {**self.data,
            'crop_slug': 'potato', 'photo': SimpleUploadedFile('leaf.png', PNG, content_type='image/png')})
        self.assertEqual(response.status_code, 302, response.context["form"].errors if response.status_code == 200 else "")
        entry = PestEntry.objects.get()
        self.assertEqual(entry.crop_slug, 'tomato')
        self.assertEqual(entry.updated_by, self.admin)
        self.assertTrue(Path(entry.photo.path).exists())
        self.client.logout()
        response = self.client.get(reverse('crops:pest_detail', args=[entry.crop_slug, entry.issue_slug]))
        for key in ['symptoms','more_info','treat_now','organic_control','chemical_control','preventive_measures']:
            self.assertContains(response, self.data[key])
        self.assertContains(response, entry.photo.url)
        cards = self.client.get(reverse('crops:pests'), {'crop': 'tomato'})
        self.assertContains(cards, entry.photo.url)
        other = self.client.get(reverse('crops:pest_detail', args=['potato','late-blight']))
        self.assertNotContains(other, self.data['symptoms'])

    def test_create_new_card_and_subsequent_edit(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('crops:pest_new'), self.data)
        self.assertEqual(response.status_code, 302, response.context["form"].errors if response.status_code == 200 else "")
        entry = PestEntry.objects.get()
        self.assertTrue(entry.issue_slug.startswith('late-blight-edited-'))
        self.assertRedirects(response, reverse('crops:pest_new', query={'crop': 'tomato'}))
        cleared = self.client.get(response.url).context['form']
        self.assertFalse(cleared.is_bound)
        self.assertEqual(cleared['crop_slug'].value(), 'tomato')
        for name in ['title', 'symptoms', 'more_info', 'treat_now', 'organic_control',
                     'chemical_control', 'preventive_measures', 'photo', 'photo_caption', 'source_url']:
            self.assertFalse(cleared[name].value(), name)
        self.assertEqual(cleared['stages'].value(), [])
        response = self.client.get(reverse('crops:pests'), {'crop': 'tomato', 'stage': 'vegetative'})
        self.assertContains(response, entry.title)
        edit_url = reverse('crops:pest_edit', args=['tomato', entry.issue_slug])
        response = self.client.post(edit_url, {**self.data, 'symptoms': '<script>alert(1)</script>'})
        self.assertEqual(PestEntry.objects.count(), 1)
        self.assertRedirects(response, reverse('crops:pest_new', query={'crop': 'tomato'}))
        public = self.client.get(reverse('crops:pest_detail', args=[entry.crop_slug, entry.issue_slug]))
        self.assertContains(public, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(public, '<script>alert(1)</script>')

    def test_invalid_image_and_missing_stage_do_not_publish(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {**self.data,
            'photo': SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')})
        self.assertEqual(response.status_code, 200)
        self.assertIn('photo', response.context['form'].errors)
        data = dict(self.data);data.pop('stages')
        response = self.client.post(self.url, data)
        self.assertIn('stages', response.context['form'].errors)
        self.assertFalse(PestEntry.objects.exists())

    def test_unknown_card_and_invalid_crop_cannot_be_saved(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(reverse('crops:pest_edit', args=['tomato','coffee-rust']), self.data).status_code, 404)
        response = self.client.post(reverse('crops:pest_new'), {**self.data, 'crop_slug': 'invalid'})
        self.assertIn('crop_slug', response.context['form'].errors)
        self.assertFalse(PestEntry.objects.exists())
