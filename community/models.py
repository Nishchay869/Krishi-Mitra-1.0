import os
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CommunityPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='community_posts'
    )
    author_session_key = models.CharField(max_length=120, blank=True, default='')
    author_name = models.CharField(_('Author name'), max_length=120, default='Farmer')
    author_location = models.CharField(_('Author location'), max_length=120, default='India')
    author_avatar = models.CharField(max_length=255, blank=True, default='')

    crop = models.CharField(_('Crop'), max_length=100, default='General')
    crop_icon = models.CharField(max_length=20, default='🌱')

    title = models.CharField(_('Question / Problem'), max_length=200)
    description = models.TextField(_('Detailed description'), max_length=2500)

    image = models.ImageField(upload_to='community/posts/', null=True, blank=True)
    image_url = models.CharField(max_length=500, blank=True, default='')

    tags = models.CharField(max_length=255, blank=True, default='')
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Community Post')
        verbose_name_plural = _('Community Posts')

    def __str__(self):
        return f"{self.crop}: {self.title[:40]}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return ''

    def get_tags(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class CommunityAnswer(models.Model):
    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='community_answers'
    )
    author_session_key = models.CharField(max_length=120, blank=True, default='')
    author_name = models.CharField(_('Author name'), max_length=120, default='Farmer')
    author_role = models.CharField(_('Role / Specialty'), max_length=80, default='Farmer')

    content = models.TextField(_('Answer / Advice'))
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    is_verified_solution = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Community Answer')
        verbose_name_plural = _('Community Answers')

    def __str__(self):
        return f"Answer by {self.author_name} on {self.post.title[:30]}"


class CommunityNotification(models.Model):
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='community_notifications'
    )
    recipient_session_key = models.CharField(max_length=120, blank=True, default='')
    recipient_name = models.CharField(max_length=120, blank=True, default='')

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    answer = models.ForeignKey(
        CommunityAnswer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    actor_name = models.CharField(max_length=120, default='Fellow Farmer')
    actor_role = models.CharField(max_length=80, default='Farmer')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Community Notification')
        verbose_name_plural = _('Community Notifications')

    def __str__(self):
        return f"Notification for {self.recipient_name or self.recipient_user}: {self.title[:30]}"
