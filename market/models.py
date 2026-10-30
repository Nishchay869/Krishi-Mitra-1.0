from django.conf import settings
from django.db import models


class MarketFavourite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    identity = models.CharField(max_length=64)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=150)
    name = models.CharField(max_length=200)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'identity'], name='unique_farmer_market_favourite')]
