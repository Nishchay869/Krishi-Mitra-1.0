from django.urls import path

from . import views

app_name = 'weather'
urlpatterns = [
    path('', views.weather_page, name='forecast'),
    path('api/', views.api_weather, name='api'),
]
