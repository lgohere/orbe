"""
URLs for feed app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'announcements', views.AnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('timeline/', views.TimelineView.as_view(), name='timeline'),
    path('posts/<int:post_id>/like/', views.LikePostView.as_view(), name='like-post'),
]