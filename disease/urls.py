from django.urls import path

from . import views

app_name = 'disease'
urlpatterns = [
    path('', views.detect_page, name='detect'),
    path('api/', views.api_detect, name='api'),
    path('history/', views.history_page, name='history'),
    path('history/<int:pk>/', views.history_detail, name='history_detail'),
    path('history/<int:pk>/delete/', views.delete_single, name='delete_single'),
    path('history/delete/', views.delete_selected, name='delete_selected'),
    path('history/delete-all/', views.delete_all, name='delete_all'),
]
