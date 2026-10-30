from django.contrib import admin
from .models import PestEntry
from .pest_forms import PestEntryForm


@admin.register(PestEntry)
class PestEntryAdmin(admin.ModelAdmin):
    form = PestEntryForm
    list_display = ['title', 'crop_slug', 'kind', 'updated_at', 'updated_by']
    list_filter = ['crop_slug', 'kind']
    search_fields = ['title', 'symptoms', 'more_info']
    readonly_fields = ['issue_slug', 'updated_at', 'updated_by']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
