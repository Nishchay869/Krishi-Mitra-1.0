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


class SafeRedisCacheTests(SimpleTestCase):
    """The Redis cache must never break a page: when Redis is down, the memory cache is used."""

    def make(self, url):
        from agri_assistant.cache import SafeRedisCache
        return SafeRedisCache(url, {'KEY_PREFIX': 'km-test', 'TIMEOUT': 60,
                                    'OPTIONS': {'socket_connect_timeout': 0.5, 'socket_timeout': 0.5}})

    def test_unreachable_redis_falls_back_to_memory_and_pauses_retries(self):
        import time
        cache = self.make('redis://127.0.0.1:1/0')            # nothing listens on port 1
        with self.assertLogs('agri_assistant.cache', 'WARNING'):
            cache.set('answer', 'Use neem oil')
        self.assertFalse(cache.redis_available)
        started = time.monotonic()
        self.assertEqual(cache.get('answer'), 'Use neem oil')  # served from memory
        self.assertEqual(cache.get_or_set('other', 'x'), 'x')
        self.assertLess(time.monotonic() - started, 0.2)         # no waiting on Redis while it is down

    def test_redis_is_tried_again_after_the_pause(self):
        from unittest.mock import patch
        from agri_assistant import cache as module
        cache = self.make('redis://127.0.0.1:1/0')
        with self.assertLogs('agri_assistant.cache', 'WARNING'):
            cache.get('x')
        with patch.object(module.time, 'monotonic', return_value=cache._down_until + 1):
            self.assertTrue(cache.redis_available)

    def test_works_with_a_real_redis_when_one_is_running(self):
        import redis
        url = 'redis://127.0.0.1:6379/15'
        try:
            redis.Redis.from_url(url, socket_connect_timeout=0.3).ping()
        except redis.RedisError:
            self.skipTest('no local Redis on 6379')
        cache = self.make(url)
        cache.set('answer', {'reply': 'ನೀಮ್ ಎಣ್ಣೆ'})
        self.assertEqual(self.make(url).get('answer'), {'reply': 'ನೀಮ್ ಎಣ್ಣೆ'})  # another process sees it
        cache.delete('answer')
