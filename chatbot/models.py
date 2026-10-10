from django.conf import settings
from django.db import models


class KnowledgeEntry(models.Model):
    """Curated, locally grounded FAQ entry. `source` records provenance (spec §4.3)."""
    INTENT_CHOICES = [
        ('crop_selection', 'Crop selection'),
        ('fertilizer', 'Fertilizer'),
        ('pest', 'Pest & disease'),
        ('scheme', 'Government scheme'),
        ('irrigation', 'Irrigation'),
        ('soil', 'Soil health'),
        ('general', 'General'),
    ]

    question = models.TextField()
    answer = models.TextField()
    intent = models.CharField(max_length=20, choices=INTENT_CHOICES, default='general')
    keywords = models.CharField(max_length=255, blank=True, help_text='Extra comma-separated match terms')
    source = models.CharField(max_length=255, help_text='Provenance, e.g. agency or portal name')
    source_url = models.URLField(blank=True)
    language = models.CharField(max_length=10, default='en')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'knowledge entries'

    def __str__(self):
        return self.question[:80]


class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=64, blank=True)
    message = models.TextField()
    message_en = models.TextField(blank=True, help_text='English translation used for matching')
    language = models.CharField(max_length=10, default='en-IN')
    is_voice = models.BooleanField(default=False)
    response = models.TextField()
    intent = models.CharField(max_length=20, blank=True)
    matched_entry = models.ForeignKey(KnowledgeEntry, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message[:60]
