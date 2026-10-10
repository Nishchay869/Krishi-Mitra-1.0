from django.contrib import admin

from .models import ChatMessage, KnowledgeEntry


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    list_display = ('question', 'intent', 'source', 'language', 'is_active')
    list_filter = ('intent', 'language', 'is_active')
    search_fields = ('question', 'answer', 'keywords')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'intent', 'confidence', 'matched_entry', 'user', 'created_at')
    list_filter = ('intent',)
    search_fields = ('message',)
    readonly_fields = [f.name for f in ChatMessage._meta.fields]
