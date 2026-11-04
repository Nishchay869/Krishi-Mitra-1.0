from django.contrib import admin
from django.utils.html import format_html
from .models import CommunityPost, CommunityAnswer, CommunityNotification


class CommunityAnswerInline(admin.TabularInline):
    model = CommunityAnswer
    extra = 0
    can_delete = True
    fields = ('author_name', 'author_role', 'content', 'likes', 'is_verified_solution', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop_badge', 'title', 'author_name', 'answers_count', 'likes', 'exact_published_time')
    list_display_links = ('id', 'title')
    list_filter = ('crop', 'created_at')
    search_fields = ('title', 'description', 'author_name', 'tags')
    date_hierarchy = 'created_at'
    inlines = [CommunityAnswerInline]
    actions = ['delete_selected', 'reset_likes']

    def crop_badge(self, obj):
        return format_html('<span>{} {}</span>', obj.crop_icon, obj.crop)
    crop_badge.short_description = 'Crop'

    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = 'Replies'

    def exact_published_time(self, obj):
        return obj.created_at.strftime('%d %b %Y, %I:%M %p')
    exact_published_time.short_description = 'Published At'

    @admin.action(description='Reset likes on selected posts')
    def reset_likes(self, request, queryset):
        queryset.update(likes=0)


@admin.register(CommunityAnswer)
class CommunityAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'author_name', 'author_role', 'post_link', 'content_snippet', 'is_verified_solution', 'likes', 'exact_time')
    list_display_links = ('id', 'author_name')
    list_filter = ('is_verified_solution', 'created_at')
    search_fields = ('content', 'author_name', 'post__title')
    date_hierarchy = 'created_at'
    actions = ['delete_selected', 'mark_verified', 'unmark_verified']

    def post_link(self, obj):
        return format_html('<a href="/admin/community/communitypost/{}/change/">{}</a>', obj.post.id, obj.post.title[:30])
    post_link.short_description = 'Question / Post'

    def content_snippet(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_snippet.short_description = 'Reply Message'

    def exact_time(self, obj):
        return obj.created_at.strftime('%d %b %Y, %I:%M %p')
    exact_time.short_description = 'Replied At'

    @admin.action(description='Mark selected replies as verified solutions')
    def mark_verified(self, request, queryset):
        queryset.update(is_verified_solution=True)

    @admin.action(description='Remove verified status from selected replies')
    def unmark_verified(self, request, queryset):
        queryset.update(is_verified_solution=False)


@admin.register(CommunityNotification)
class CommunityNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_info', 'actor_name', 'title', 'is_read', 'exact_time')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient_name')
    date_hierarchy = 'created_at'
    actions = ['delete_selected', 'mark_as_read']

    def recipient_info(self, obj):
        return obj.recipient_name or (obj.recipient_user.username if obj.recipient_user else 'Guest Farmer')
    recipient_info.short_description = 'Recipient'

    def exact_time(self, obj):
        return obj.created_at.strftime('%d %b %Y, %I:%M %p')
    exact_time.short_description = 'Sent At'

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
