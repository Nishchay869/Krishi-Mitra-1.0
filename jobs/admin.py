from django.contrib import admin

from .models import BackgroundJob


@admin.register(BackgroundJob)
class BackgroundJobAdmin(admin.ModelAdmin):
    list_display = ('task_path', 'status', 'attempts', 'run_after', 'enqueued_at', 'finished_at')
    list_filter = ('status', 'task_path')
    readonly_fields = [f.name for f in BackgroundJob._meta.fields]
