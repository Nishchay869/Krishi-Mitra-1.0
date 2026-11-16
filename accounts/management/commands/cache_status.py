"""Show which cache is in use and whether it works: python manage.py cache_status"""
import time

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check the cache (Redis or memory) with a write/read round trip.'

    def handle(self, *args, **options):
        backend = settings.CACHES['default']['BACKEND'].rsplit('.', 1)[-1]
        self.stdout.write(f'Cache backend: {backend}')
        if not getattr(settings, 'REDIS_URL', ''):
            self.stdout.write('REDIS_URL is not set: each server process uses its own memory cache.')
        start = time.monotonic()
        cache.set('cache_status:ping', 'pong', 30)
        ok = cache.get('cache_status:ping') == 'pong'
        ms = (time.monotonic() - start) * 1000
        if getattr(cache, 'redis_available', True) is False:
            self.stdout.write(self.style.WARNING('Redis is unreachable right now; using the memory fallback.'))
        elif ok:
            self.stdout.write(self.style.SUCCESS(f'Write + read OK in {ms:.0f} ms'))
        else:
            self.stdout.write(self.style.ERROR('Write + read failed'))
