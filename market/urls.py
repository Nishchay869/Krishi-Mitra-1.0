from django.urls import path

from . import views, actions
from .local_prices import local_prices_page

app_name = 'market'
urlpatterns = [
    path('favourite/', actions.favourite, name='favourite'),
    path('location/', actions.location, name='location'),
    path('', local_prices_page, name='prices'),
    path('overview/', views.prices_page, name='overview'),
    path('api/', views.api_prices, name='api'),
]
