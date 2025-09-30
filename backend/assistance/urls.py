"""
URL configuration for the assistance module.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssistanceCaseViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'cases', AssistanceCaseViewSet, basename='assistancecase')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]