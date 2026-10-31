from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_FARMER = 'farmer'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [(ROLE_FARMER, 'Farmer'), (ROLE_ADMIN, 'Administrator')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_FARMER)
    village = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    phone = models.CharField(max_length=15, blank=True)
    selected_crops = models.JSONField(default=list, blank=True)
    growing_place = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.user.is_staff

    @property
    def location_query(self):
        """Prefer the saved village when a caller needs a place name."""
        return next((value.strip() for value in (self.village, self.district, self.state) if value.strip()), '')


class PredictionLog(models.Model):
    """ML prediction log (spec §2.3) shared by crop recommendation, yield prediction and disease detection."""
    KIND_CROP = 'crop'
    KIND_DISEASE = 'disease'
    KIND_YIELD = 'yield'
    KIND_CHOICES = [(KIND_CROP, 'Crop recommendation'), (KIND_DISEASE, 'Disease detection'),
                    (KIND_YIELD, 'Yield prediction')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    inputs = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_kind_display()} @ {self.created_at:%Y-%m-%d %H:%M}'


class Feedback(models.Model):
    """User experience feedback for Krishi Mitra app."""
    RATING_BAD = 'bad'
    RATING_AVERAGE = 'average'
    RATING_GOOD = 'good'
    RATING_CHOICES = [
        (RATING_BAD, 'Bad'),
        (RATING_AVERAGE, 'Average'),
        (RATING_GOOD, 'Good'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Feedback'
        verbose_name_plural = 'User Feedbacks'

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f'{user_str} — {self.get_rating_display()} ({self.created_at:%d %b %Y})'

