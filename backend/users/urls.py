"""
URLs for users app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'invitations', views.InvitationViewSet, basename='invitation')
router.register(r'members', views.MemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('roles/', views.UserRoleListView.as_view(), name='user-roles'),
    path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
    path('onboarding/status/', views.OnboardingStatusView.as_view(), name='onboarding-status'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
]