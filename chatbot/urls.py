from django.urls import path

from . import views

app_name = 'chatbot'
urlpatterns = [
    path('', views.chat_page, name='chat'),
    path('api/', views.api_chat, name='api'),
    path('api/voice/', views.api_voice, name='voice'),
    path('api/transcribe/', views.api_transcribe, name='transcribe'),
    path('api/speak/<int:pk>/', views.api_speak, name='speak'),
    path('api/greeting/', views.api_greeting, name='greeting'),
    path('api/clear/', views.api_clear, name='clear'),
]
