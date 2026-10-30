from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def pest_photo_path(instance, filename):
    return f'pests/{uuid4().hex}{Path(filename).suffix.lower()}'


def validate_photo_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Upload a photograph smaller than 5 MB.')


class PestEntry(models.Model):
    """An administrator's crop-specific replacement or new library card."""
    crop_slug = models.SlugField(max_length=100)
    issue_slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=40)
    stages = models.JSONField(default=list)
    symptoms = models.TextField(blank=True)
    more_info = models.TextField('More information', blank=True)
    treat_now = models.TextField(blank=True)
    organic_control = models.TextField(blank=True)
    chemical_control = models.TextField(blank=True)
    preventive_measures = models.TextField(blank=True)
    photo = models.ImageField(upload_to=pest_photo_path, blank=True,
        validators=[validate_photo_size, FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])])
    photo_caption = models.CharField(max_length=300, blank=True)
    source_url = models.URLField('Reference link', blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pest_entries')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['crop_slug', 'issue_slug'], name='unique_crop_pest_entry')]
        ordering = ['crop_slug', 'title']

    def __str__(self):
        return f'{self.title} ({self.crop_slug})'
