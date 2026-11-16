"""Background jobs stored in the database (free: no Redis or separate worker server needed)."""
from django.db import models


class BackgroundJob(models.Model):
    class Status(models.TextChoices):
        READY = 'READY', 'Ready'
        RUNNING = 'RUNNING', 'Running'
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'

    id = models.CharField(primary_key=True, max_length=32, editable=False)
    task_path = models.CharField(max_length=255)          # e.g. "accounts.tasks.send_email"
    args = models.JSONField(default=list)
    kwargs = models.JSONField(default=dict)
    queue_name = models.CharField(max_length=64, default='default')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.READY, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    run_after = models.DateTimeField(db_index=True)       # earliest time the job may run (retries back off)
    enqueued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    worker_id = models.CharField(max_length=64, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        ordering = ['run_after', 'enqueued_at']
        indexes = [models.Index(fields=['status', 'run_after'])]

    def __str__(self):
        return f'{self.task_path} [{self.status}]'
