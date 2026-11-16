"""Redis cache that never takes the site down.

Cached data (Gemini answers, translations, voice replies, weather, mandi prices) is kept in Redis,
so it survives the free server sleeping, restarting and redeploying. If Redis is unreachable or
slow, every call quietly uses an in-process memory cache instead (as before Redis was added), and
Redis is tried again 30 seconds later, so a Redis outage costs a few cache misses, not errors.
"""
import logging
import time

from django.core.cache.backends.locmem import LocMemCache
from django.core.cache.backends.redis import RedisCache

logger = logging.getLogger(__name__)

RETRY_AFTER_SECONDS = 30

# Cache calls that talk to Redis; each falls back to the memory cache on failure.
_WRAPPED = ('add', 'get', 'set', 'touch', 'delete', 'get_many', 'set_many', 'delete_many',
            'has_key', 'incr', 'clear')


class SafeRedisCache(RedisCache):
    def __init__(self, server, params):
        super().__init__(server, params)
        self._fallback = LocMemCache('redis-fallback', {
            'TIMEOUT': params.get('TIMEOUT', 300), 'KEY_PREFIX': params.get('KEY_PREFIX', ''),
            'OPTIONS': {'MAX_ENTRIES': 1000},
        })
        self._down_until = 0.0

    @property
    def redis_available(self):
        return time.monotonic() >= self._down_until

    def _call(self, name, *args, **kwargs):
        if self.redis_available:
            import redis
            try:
                return getattr(super(), name)(*args, **kwargs)
            except (redis.ConnectionError, redis.TimeoutError) as exc:
                # Unreachable/slow: stop trying for a while so pages don't wait on timeouts.
                self._down_until = time.monotonic() + RETRY_AFTER_SECONDS
                logger.warning('Redis cache unavailable (%s); using memory cache for %ss',
                               type(exc).__name__, RETRY_AFTER_SECONDS)
            except redis.RedisError as exc:
                # One bad command (e.g. value too large): fall back for this call only.
                logger.warning('Redis cache %s failed (%s); using memory cache', name, type(exc).__name__)
        return getattr(self._fallback, name)(*args, **kwargs)


def _make(name):
    def method(self, *args, **kwargs):
        return self._call(name, *args, **kwargs)
    method.__name__ = name
    return method


for _name in _WRAPPED:
    setattr(SafeRedisCache, _name, _make(_name))
