from django.contrib import admin
from .models import PestEntry, CropStatus, FertilizerPreset
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


@admin.register(FertilizerPreset)
class FertilizerPresetAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'preset_key', 'mode', 'nitrogen', 'phosphorus', 'potassium', 'scope', 'updated_at', 'updated_by']
    list_editable = ['nitrogen', 'phosphorus', 'potassium']
    list_filter = ['mode']
    search_fields = ['crop_name', 'preset_key', 'scope']
    readonly_fields = ['updated_at', 'updated_by']

    class Media:
        css = {
            'all': ('css/admin_fertilizer_preset.css',)
        }

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()


