from django.contrib import admin

from .models import PredictionLog, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'district', 'state', 'preferred_language')
    list_filter = ('role', 'state', 'preferred_language')
    search_fields = ('user__username', 'district', 'village')


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('kind', 'user', 'created_at')
    list_filter = ('kind',)
    readonly_fields = ('user', 'kind', 'inputs', 'result', 'created_at')
