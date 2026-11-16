"""Django Tasks backend that stores jobs in the database (see jobs.worker for running them).

Use Django's standard API:

    from django.tasks import task

    @task
    def send_email(subject, body, recipients): ...

    send_email.enqueue('Hi', 'Body', ['farmer@example.com'])   # returns immediately
"""
from django.db import transaction
from django.tasks.backends.base import BaseTaskBackend
from django.tasks.base import TaskError, TaskResult, TaskResultStatus
from django.tasks.exceptions import TaskResultDoesNotExist
from django.tasks.signals import task_enqueued
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.json import normalize_json
from django.utils.module_loading import import_string

from . import worker
from .models import BackgroundJob


class DatabaseBackend(BaseTaskBackend):
    supports_defer = True
    supports_get_result = True

    def enqueue(self, task, args, kwargs):
        self.validate_task(task)
        job = BackgroundJob.objects.create(
            id=get_random_string(32),
            task_path=task.module_path,
            args=normalize_json(list(args)),
            kwargs=normalize_json(dict(kwargs)),
            queue_name=task.queue_name,
            run_after=task.run_after or timezone.now(),
        )
        # Wake the in-process worker once the job is really saved (not before the commit).
        transaction.on_commit(worker.wake)
        result = self._result(job, task)
        task_enqueued.send(type(self), task_result=result)
        return result

    def get_result(self, result_id):
        try:
            job = BackgroundJob.objects.get(pk=result_id)
        except BackgroundJob.DoesNotExist:
            raise TaskResultDoesNotExist(result_id) from None
        return self._result(job, import_string(job.task_path))

    def _result(self, job, task):
        errors = []
        if job.status == BackgroundJob.Status.FAILED and job.last_error:
            errors.append(TaskError(exception_class_path='', traceback=job.last_error))
        return TaskResult(
            task=task, id=job.id, status=TaskResultStatus(job.status),
            enqueued_at=job.enqueued_at, started_at=job.started_at, finished_at=job.finished_at,
            last_attempted_at=job.started_at, args=job.args, kwargs=job.kwargs,
            backend=self.alias, errors=errors, worker_ids=[job.worker_id] if job.worker_id else [],
        )
