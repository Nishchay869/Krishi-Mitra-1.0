"""Generate missing UI catalogs once, never while a farmer loads a page."""
import importlib.util
import json
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.languages import LANGUAGE_CODES


class Command(BaseCommand):
    help = 'Generate missing translations for 22 scheduled languages. Uses only a local model; no API credits.'

    def add_arguments(self, parser):
        parser.add_argument('--model', default=str(settings.BASE_DIR / '.offline-models/sarvam-translate-4bit'))
        parser.add_argument('--python', default=str(settings.BASE_DIR / '.venv-translate/bin/python'))
        parser.add_argument('--languages', nargs='+', choices=sorted(LANGUAGE_CODES - {'en'}))
        parser.add_argument('--status', action='store_true', help='Show catalog readiness without making API calls.')

    def handle(self, *args, **options):
        folder = Path(settings.BASE_DIR) / 'locale/ui'
        source = json.loads((folder / 'en.json').read_text())
        languages = options['languages'] or sorted(LANGUAGE_CODES - {'en'})
        if options['status']:
            for code in languages:
                path = folder / f'{code}.json'
                data = json.loads(path.read_text()) if path.exists() else {}
                count = sum(bool(data.get(key)) for key in source)
                self.stdout.write(f'{code}: {count}/{len(source)} messages')
            return
        needs_generation = any(not (folder / f'{code}.json').exists() or
                               not all(json.loads((folder / f'{code}.json').read_text()).get(key) for key in source)
                               for code in languages)
        if needs_generation:
            executable = Path(options['python']).resolve()
            if not executable.is_file():
                raise CommandError('Local translation environment is missing. Follow README offline setup; no API credentials are needed.')
            command = [str(executable), '-u', str(settings.BASE_DIR / 'scripts/translate_ui_offline.py'),
                       '--model', str(Path(options['model']).resolve()), '--languages', *languages]
            result = subprocess.run(command, cwd=settings.BASE_DIR)
            if result.returncode:
                raise CommandError('Local generation stopped. Saved drafts can be resumed without API credits.')
        spec = importlib.util.spec_from_file_location('build_translations', settings.BASE_DIR / 'scripts/build_translations.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.build()
        self.stdout.write(self.style.SUCCESS('Local catalogs compiled. Restart Django to enable completed languages.'))
