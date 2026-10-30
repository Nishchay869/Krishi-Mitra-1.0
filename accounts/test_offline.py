import json
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase


class OfflineAssetTests(TestCase):
    def test_pages_use_local_styles_scripts_and_icons(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'cdn.jsdelivr.net')
        self.assertContains(response, '/static/vendor/bootstrap/bootstrap.min.css')
        self.assertContains(response, '/static/js/offline-client.js')

    @patch('socket.socket', side_effect=AssertionError('Network access forbidden'))
    def test_language_display_and_worker_do_not_require_network(self, socket):
        self.client.cookies['django_language'] = 'kn'
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Language'], 'kn')
        worker = self.client.get('/service-worker.js')
        self.assertEqual(worker.status_code, 200)
        self.assertContains(worker, 'const APP_VERSION')
        self.assertEqual(worker['Service-Worker-Allowed'], '/')

    def test_offline_manifest_contains_complete_local_packs(self):
        root = settings.BASE_DIR / 'static/i18n'
        manifest = json.loads((root / 'manifest.json').read_text())
        source = json.loads((root / 'en.json').read_text())
        for language in manifest['languages']:
            pack = json.loads((root / f"{language['code']}.json").read_text())
            self.assertEqual(source.keys(), pack.keys())
            self.assertTrue(all(pack.values()))
