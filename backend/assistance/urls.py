"""
URLs for assistance app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cases', views.AssistanceCaseViewSet)
router.register(r'attachments', views.AttachmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cases/<int:case_id>/approve/', views.ApproveCaseView.as_view(), name='approve-case'),
    path('cases/<int:case_id>/reject/', views.RejectCaseView.as_view(), name='reject-case'),
    path('pending-approval/', views.PendingApprovalView.as_view(), name='pending-approval'),
]