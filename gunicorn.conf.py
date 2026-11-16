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
    # Patch before the app is loaded. Render passes its own GUNICORN_CMD_ARGS including
    # --preload, which imports Django in the master process *before* the gevent worker would
    # patch; Django's DB connections then live in a real threading.local shared by every
    # request ("DatabaseWrapper objects created in a thread can only be used in that same
    # thread" -> every page 500). Patching here, first, keeps them per request.
    from gevent import monkey
    monkey.patch_all()
    worker_class = 'gevent'
    worker_connections = 50


def post_worker_init(worker):
    """Start the background-job worker in each server process (also runs jobs left from a restart)."""
    from jobs.worker import ensure_started
    ensure_started()
