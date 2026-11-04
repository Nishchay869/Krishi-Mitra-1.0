from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('ask/', views.ask_community_view, name='ask'),
    path('post/<int:post_id>/', views.post_detail_view, name='detail'),
    path('post/<int:post_id>/answer/', views.post_answer_view, name='answer'),
    path('post/<int:post_id>/vote/', views.post_vote_view, name='vote'),
    path('post/<int:post_id>/translate/', views.post_translate_view, name='translate'),
    path('answer/<int:answer_id>/vote/', views.answer_vote_view, name='answer_vote'),
    path('api/notifications/', views.notifications_api_view, name='notifications_api'),
    path('api/notifications/read/', views.mark_notifications_read_view, name='notifications_read'),
]
