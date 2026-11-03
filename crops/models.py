from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def pest_photo_path(instance, filename):
    return f'pests/{uuid4().hex}{Path(filename).suffix.lower()}'


def crop_status_photo_path(instance, filename):
    return f'crop_statuses/{uuid4().hex}{Path(filename).suffix.lower()}'


def validate_photo_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Upload a photograph smaller than 5 MB.')


class CropStatus(models.Model):
    """Instagram-style status/story uploaded by agronomists/admins for specific crops."""
    BADGE_ALERT = 'alert'
    BADGE_ADVISORY = 'advisory'
    BADGE_SPRAY = 'spray'
    BADGE_TIP = 'tip'
    BADGE_WEATHER = 'weather'
    BADGE_CHOICES = [
        (BADGE_ALERT, 'Disease / Pest Alert'),
        (BADGE_ADVISORY, 'Crop Advisory'),
        (BADGE_SPRAY, 'Spraying Window'),
        (BADGE_TIP, 'Farming Tip'),
        (BADGE_WEATHER, 'Weather Warning'),
    ]

    crop_name = models.CharField(max_length=100)
    crop_slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default=BADGE_ADVISORY)
    photo = models.ImageField(upload_to=crop_status_photo_path, blank=True, null=True,
        validators=[validate_photo_size, FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])])
    photo_url = models.URLField(max_length=500, blank=True, help_text='Fallback or external image URL')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='crop_statuses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crop Status / Story'
        verbose_name_plural = 'Crop Statuses / Stories'

    def __str__(self):
        return f'{self.crop_name}: {self.title} ({self.created_at:%d %b %H:%M})'

    @property
    def image_url(self):
        if self.photo:
            try:
                return self.photo.url
            except Exception:
                pass
        if self.photo_url:
            return self.photo_url
        slug = self.crop_slug or 'crop'
        return f'/static/images/crops/{slug}.webp'


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


class FertilizerPreset(models.Model):
    """Database-backed N-P-K nutrient recommendation preset editable by administrators."""
    preset_key = models.CharField(max_length=60, unique=True, db_index=True,
                                  help_text='Unique identifier matching the preset (e.g. tomato, rice, mango-1)')
    crop_name = models.CharField(max_length=100)
    mode = models.CharField(max_length=20, default='plants',
                            choices=[('plants', 'Plants (field/kg/ha)'), ('trees', 'Trees (grams/tree)')])
    nitrogen = models.DecimalField(max_digits=8, decimal_places=2,
                                   help_text='Recommended Nitrogen (N) rate (kg/ha or g/tree)')
    phosphorus = models.DecimalField(max_digits=8, decimal_places=2,
                                     help_text='Recommended Phosphate (P2O5) rate (kg/ha or g/tree)')
    potassium = models.DecimalField(max_digits=8, decimal_places=2,
                                    help_text='Recommended Potash (K2O) rate (kg/ha or g/tree)')
    scope = models.CharField(max_length=255, blank=True,
                             help_text='Application scope, variety, or tree age note')
    source = models.URLField(max_length=500, blank=True,
                             help_text='Agronomic source reference')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='fertilizer_presets')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['crop_name', 'preset_key']
        verbose_name = 'Fertilizer N-P-K Preset'
        verbose_name_plural = 'Fertilizer N-P-K Presets'

    def __str__(self):
        return f'{self.crop_name} ({self.preset_key}): N={self.nitrogen} P={self.phosphorus} K={self.potassium}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            from .fertilizer_presets import update_preset_in_memory
            update_preset_in_memory(
                self.preset_key,
                self.nitrogen,
                self.phosphorus,
                self.potassium,
                crop=self.crop_name,
                scope=self.scope,
            )
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete('effective_fertilizer_presets')
        super().delete(*args, **kwargs)

