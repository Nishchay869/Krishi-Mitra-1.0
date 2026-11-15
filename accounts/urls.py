from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

app_name = 'accounts'
urlpatterns = [
    path('onboarding/', views.onboarding, name='onboarding'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_redirect, name='admin_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Forgot password: email link -> set new password
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html', form_class=StyledPasswordResetForm,
        email_template_name='accounts/password_reset_email.txt',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done')), name='password_reset'),
    path('password-reset/sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html', form_class=StyledSetPasswordForm,
        success_url=reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/api/', views.settings_api, name='settings_api'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-status/upload/', views.admin_upload_status, name='admin_upload_status'),
    path('admin-status/<int:status_id>/delete/', views.admin_delete_status, name='admin_delete_status'),
]
