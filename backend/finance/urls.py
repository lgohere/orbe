"""
URLs for finance app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fees', views.MembershipFeeViewSet, basename='membership-fee')
router.register(r'voluntary-donations', views.VoluntaryDonationViewSet, basename='voluntary-donation')
router.register(r'donation-requests', views.DonationRequestViewSet, basename='donation-request')

urlpatterns = [
    path('', include(router.urls)),
]