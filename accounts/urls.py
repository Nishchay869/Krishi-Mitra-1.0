from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailLoginForm

app_name = 'accounts'
urlpatterns = [
    path('onboarding/', views.onboarding, name='onboarding'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',
                                                authentication_form=EmailLoginForm,
                                                redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/api/', views.settings_api, name='settings_api'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
