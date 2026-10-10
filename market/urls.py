from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
    path('', views.prices_page, name='prices'),
    path('api/', views.api_prices, name='api'),
]
