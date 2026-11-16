from django.core.management.base import BaseCommand

from jobs.worker import run_pending


class Command(BaseCommand):
    help = 'Run due background jobs once (the web server normally runs them by itself).'

    def handle(self, *args, **options):
        self.stdout.write(f'Ran {run_pending(limit=500)} background job(s).')
