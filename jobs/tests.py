from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.tasks import task
from django.tasks.base import TaskResultStatus
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import BackgroundJob
from .worker import run_pending

CALLS = []


@task
def record(value):
    CALLS.append(value)


@task
def always_fails():
    raise RuntimeError('mail server down')


DB_TASKS = {'default': {'BACKEND': 'jobs.backend.DatabaseBackend'}}


@override_settings(TASKS=DB_TASKS, JOBS_RUN_IN_PROCESS=False)
class DatabaseQueueTests(TestCase):
    def setUp(self):
        CALLS.clear()

    def test_enqueue_returns_immediately_and_worker_runs_it(self):
        result = record.enqueue('hello')
        self.assertEqual(CALLS, [])                                  # not run during the request
        self.assertEqual(BackgroundJob.objects.get(pk=result.id).status, 'READY')
        self.assertEqual(run_pending(), 1)
        self.assertEqual(CALLS, ['hello'])
        self.assertEqual(record.get_backend().get_result(result.id).status, TaskResultStatus.SUCCESSFUL)

    def test_failed_job_retries_with_backoff_then_gives_up(self):
        result = always_fails.enqueue()
        run_pending()
        job = BackgroundJob.objects.get(pk=result.id)
        self.assertEqual((job.status, job.attempts), ('READY', 1))
        self.assertGreater(job.run_after, timezone.now() + timedelta(seconds=20))   # waits ~30 s
        self.assertIn('mail server down', job.last_error)
        for _ in range(2):                                           # pretend the waits passed
            BackgroundJob.objects.filter(pk=job.pk).update(run_after=timezone.now())
            run_pending()
        job.refresh_from_db()
        self.assertEqual((job.status, job.attempts), ('FAILED', 3))
        self.assertEqual(run_pending(), 0)                          # never retried again

    def test_job_stuck_by_a_crashed_server_is_retried(self):
        result = record.enqueue('again')
        BackgroundJob.objects.filter(pk=result.id).update(
            status='RUNNING', started_at=timezone.now() - timedelta(hours=1))
        run_pending()
        self.assertEqual(CALLS, ['again'])

    def test_deferred_job_waits_for_its_time(self):
        record.using(run_after=timezone.now() + timedelta(hours=1)).enqueue('later')
        self.assertEqual(run_pending(), 0)

    def test_password_reset_email_is_sent_in_the_background(self):
        from django.contrib.auth.models import User
        User.objects.create_user('bg-farmer', email='bg@example.com', password='Bg-Pass-1234!')
        self.client.post('/accounts/password-reset/', {'email': 'bg@example.com'})
        self.assertEqual(len(mail.outbox), 0)                        # page answered without waiting
        run_pending()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/password-reset/', mail.outbox[0].body)
