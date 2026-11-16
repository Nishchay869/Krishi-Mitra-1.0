import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class StaticReferencesTests(SimpleTestCase):
    """Production uses fingerprinted static files (ManifestStaticFilesStorage): a template that
    points at a missing file makes the whole page fail with a 500, not just a broken image."""

    def test_every_static_file_named_in_a_template_exists(self):
        pattern = re.compile(r"""{%\s*static\s+['"]([^'"]+)['"]""")
        static_dirs = [Path(d) for d in settings.STATICFILES_DIRS]
        missing = []
        for template in (Path(settings.BASE_DIR) / 'templates').rglob('*.html'):
            for name in pattern.findall(template.read_text(encoding='utf-8')):
                if not any((d / name).exists() for d in static_dirs):
                    missing.append(f'{template.relative_to(settings.BASE_DIR)}: {name}')
        self.assertEqual(missing, [], 'Templates reference static files that do not exist')
