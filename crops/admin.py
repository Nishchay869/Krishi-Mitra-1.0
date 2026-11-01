from django.contrib import admin
from .models import PestEntry, CropStatus
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


@admin.register(CropStatus)
class CropStatusAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'title', 'badge', 'is_active', 'created_at', 'expires_at', 'author']
    list_filter = ['crop_slug', 'badge', 'is_active']
    search_fields = ['crop_name', 'title', 'caption']
    readonly_fields = ['created_at', 'author']

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
