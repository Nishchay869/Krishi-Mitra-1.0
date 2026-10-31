from django.contrib import admin

from .models import Feedback, PredictionLog, Profile


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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
