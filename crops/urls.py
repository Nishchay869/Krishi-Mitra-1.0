from django.urls import path

from . import views

app_name = 'crops'
urlpatterns = [
    path('', views.recommend_page, name='recommend'),
    path('api/', views.api_recommend, name='api'),
    path('yield/', views.yield_page, name='yield'),
    path('yield/api/', views.api_yield, name='yield_api'),
]
