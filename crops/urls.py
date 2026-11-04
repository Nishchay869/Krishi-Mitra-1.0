from django.urls import path

from . import views
from . import library_views, pest_views, pest_admin_views

app_name = 'crops'
urlpatterns = [
    path('fertilizer/shops/', views.fertilizer_shops, name='fertilizer_shops'),
    path('fertilizer/application/<slug:combination>/', views.fertilizer_application, name='fertilizer_application'),
    path('fertilizer/manage/', views.fertilizer_manage, name='fertilizer_manage'),
    path('fertilizer/manage/save/', views.fertilizer_preset_save, name='fertilizer_preset_save'),
    path('fertilizer/', views.fertilizer_page, name='fertilizer'),
    path('pesticide/', views.pesticide_calculator, name='pesticide_calculator'),
    path('library/', library_views.index, name='library'),
    path('library/pests/manage/', pest_admin_views.index, name='pest_admin'),
    path('library/pests/manage/new/', pest_admin_views.edit, name='pest_new'),
    path('library/pests/manage/<slug:crop_slug>/<slug:issue_slug>/', pest_admin_views.edit, name='pest_edit'),
    path('library/pests/', pest_views.index, name='pests'),
    path('library/pests/<slug:crop_slug>/<slug:issue_slug>/', pest_views.detail, name='pest_detail'),
    path('library/<slug:slug>/', library_views.detail, name='library_detail'),
    path('', views.recommend_page, name='recommend'),
    path('api/', views.api_recommend, name='api'),
    path('yield/', views.yield_page, name='yield'),
    path('yield/api/', views.api_yield, name='yield_api'),
    path('yield/agronomy/', views.api_agronomy, name='agronomy_api'),
    path('api/crop-vision/diagnose/', views.api_crop_vision_diagnose, name='crop_vision_diagnose'),
]
