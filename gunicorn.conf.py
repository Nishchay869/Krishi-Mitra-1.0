"""Gunicorn settings (loaded automatically from the project root).

Use gevent workers when gevent imports cleanly: while one request waits on Gemini, Sarvam,
weather or data.gov.in, the worker serves others (load test: 40 slow requests 22.5s -> 4.7s).
If gevent cannot be loaded on a host, fall back to threads instead of failing to start,
and log why so it can be fixed.
"""
import os
import sys

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
timeout = 60
workers = int(os.environ.get('WEB_CONCURRENCY', '1'))

try:
    import gevent  # noqa: F401
    from gunicorn.workers import ggevent  # noqa: F401  (the worker class gunicorn will load)
except Exception as exc:  # ImportError, or a broken binary wheel
    print(f'[gunicorn.conf] gevent unavailable ({type(exc).__name__}: {exc}); using 4 threads instead',
          file=sys.stderr, flush=True)
    worker_class = 'gthread'
    threads = 4
else:
    worker_class = 'gevent'
    worker_connections = 50
