"""Runs background jobs inside the web server process (free hosting: no separate worker service).

- Starts on the first enqueue in a process, and when gunicorn starts a worker (leftover jobs).
- Wakes immediately when a job is added; otherwise checks for due retries now and then.
- Failed jobs retry with growing delays (30 s, 60 s, ...) up to max_attempts.
- Jobs left RUNNING by a crashed/restarted server are retried.
- Claiming is an atomic UPDATE, so several server processes never run the same job twice.
- Database connections are closed between rounds so an idle server does not keep the
  (free, auto-suspending) Postgres database awake.
"""
import logging
import os
import socket
import threading
import traceback
from datetime import timedelta

from django.conf import settings
from django.db import connections
from django.db.models import F, Min
from django.utils import timezone
from django.utils.module_loading import import_string

from .models import BackgroundJob

logger = logging.getLogger(__name__)

WORKER_ID = f'{socket.gethostname()}-{os.getpid()}'[:64]
IDLE_WAIT_SECONDS = 300          # nothing to do: look again after 5 minutes (or when woken)
RETRY_BASE_SECONDS = 30
STALE_AFTER = timedelta(minutes=10)

_wake = threading.Event()
_lock = threading.Lock()
_started_pid = None


def ensure_started():
    """Start the background worker in this process (once)."""
    global _started_pid
    if not getattr(settings, 'JOBS_RUN_IN_PROCESS', True):
        return
    with _lock:
        if _started_pid == os.getpid():
            return
        _started_pid = os.getpid()
    threading.Thread(target=_loop, name='background-jobs', daemon=True).start()


def wake():
    ensure_started()
    _wake.set()


def run_pending(limit=50):
    """Run due jobs now; returns how many ran. Used by the worker, tests and `manage.py run_jobs`."""
    _retry_stale()
    done = 0
    while done < limit:
        job = _claim_next()
        if job is None:
            break
        _execute(job)
        done += 1
    return done


def _claim_next():
    now = timezone.now()
    due = BackgroundJob.objects.filter(status=BackgroundJob.Status.READY, run_after__lte=now)
    for job_id in due.values_list('id', flat=True)[:5]:
        claimed = BackgroundJob.objects.filter(pk=job_id, status=BackgroundJob.Status.READY).update(
            status=BackgroundJob.Status.RUNNING, started_at=now, worker_id=WORKER_ID, attempts=F('attempts') + 1)
        if claimed == 1:
            return BackgroundJob.objects.get(pk=job_id)
    return None


def _execute(job):
    now = timezone.now
    try:
        import_string(job.task_path).call(*job.args, **job.kwargs)
    except Exception:  # noqa: BLE001 - a job must never take the worker down
        error = traceback.format_exc()[-4000:]
        if job.attempts < job.max_attempts:
            delay = RETRY_BASE_SECONDS * 2 ** (job.attempts - 1)
            BackgroundJob.objects.filter(pk=job.pk).update(
                status=BackgroundJob.Status.READY, run_after=now() + timedelta(seconds=delay), last_error=error)
            logger.warning('Background job %s failed (attempt %s/%s), retrying in %ss',
                           job.task_path, job.attempts, job.max_attempts, delay)
        else:
            BackgroundJob.objects.filter(pk=job.pk).update(
                status=BackgroundJob.Status.FAILED, finished_at=now(), last_error=error)
            logger.error('Background job %s failed permanently after %s attempts:\n%s',
                         job.task_path, job.attempts, error)
    else:
        BackgroundJob.objects.filter(pk=job.pk).update(
            status=BackgroundJob.Status.SUCCESSFUL, finished_at=now(), last_error='')


def _retry_stale():
    BackgroundJob.objects.filter(status=BackgroundJob.Status.RUNNING,
                                 started_at__lt=timezone.now() - STALE_AFTER).update(status=BackgroundJob.Status.READY)


def _seconds_until_next_job():
    earliest = BackgroundJob.objects.filter(status=BackgroundJob.Status.READY).aggregate(t=Min('run_after'))['t']
    if earliest is None:
        return IDLE_WAIT_SECONDS
    return min(IDLE_WAIT_SECONDS, max(1.0, (earliest - timezone.now()).total_seconds()))


def _loop():
    while True:
        wait = IDLE_WAIT_SECONDS
        try:
            run_pending()
            wait = _seconds_until_next_job()
        except Exception:  # noqa: BLE001
            logger.exception('Background job worker error')
        finally:
            connections.close_all()
        _wake.wait(wait)
        _wake.clear()
