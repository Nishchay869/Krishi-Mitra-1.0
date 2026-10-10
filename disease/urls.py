from django.urls import path

from . import views

app_name = 'disease'
urlpatterns = [
    path('', views.detect_page, name='detect'),
    path('api/', views.api_detect, name='api'),
]
