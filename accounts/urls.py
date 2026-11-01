from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('onboarding/', views.onboarding, name='onboarding'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_redirect, name='admin_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/api/', views.settings_api, name='settings_api'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-status/upload/', views.admin_upload_status, name='admin_upload_status'),
    path('admin-status/<int:status_id>/delete/', views.admin_delete_status, name='admin_delete_status'),
]
