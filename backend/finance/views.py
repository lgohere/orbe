from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from .models import MembershipFee, Donation
from .serializers import (
    MembershipFeeSerializer,
    MembershipFeeUpdateSerializer,
    DonationSerializer,
    DonationCreateSerializer
)


class IsBoardOrAdmin(permissions.BasePermission):
    """Allow only Board members and Super Admins"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role in ['SUPER_ADMIN', 'BOARD']
        )


class MembershipFeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for membership fees.
    - List/Retrieve: Members see their own, Board/Admin see all
    - Create/Update/Delete: Board/Admin only
    """
    serializer_class = MembershipFeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter fees based on user role"""
        user = self.request.user
        if user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return MembershipFee.objects.all().select_related('user')
        else:
            # Regular members only see their own fees
            return MembershipFee.objects.filter(user=user)

    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.action in ['update', 'partial_update']:
            return MembershipFeeUpdateSerializer
        return MembershipFeeSerializer

    def get_permissions(self):
        """Only Board/Admin can create/update/delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBoardOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def mark_paid(self, request, pk=None):
        """Mark a membership fee as paid"""
        fee = self.get_object()
        fee.status = 'paid'
        fee.paid_at = timezone.now()
        fee.save()
        serializer = self.get_serializer(fee)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_fees(self, request):
        """Get current user's membership fees"""
        fees = MembershipFee.objects.filter(user=request.user).order_by('-competency_month')
        serializer = self.get_serializer(fees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue fees (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view all overdue fees'},
                status=status.HTTP_403_FORBIDDEN
            )

        overdue_fees = MembershipFee.objects.filter(
            status='overdue'
        ).select_related('user').order_by('-due_date')

        serializer = self.get_serializer(overdue_fees, many=True)
        return Response(serializer.data)


class DonationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for donations.
    - List: All authenticated users (respects anonymity)
    - Create: All users (including anonymous if allowed)
    - Update/Delete: Board/Admin only
    """
    queryset = Donation.objects.all().order_by('-donated_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return DonationCreateSerializer
        return DonationSerializer

    def get_queryset(self):
        """Filter based on user permissions"""
        user = self.request.user
        queryset = Donation.objects.all()

        # Board/Admin see all donations including internal data
        if user.is_authenticated and user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return queryset.select_related('user')

        # Regular users see only public donations
        return queryset.filter(is_anonymous=False).select_related('user')

    def get_permissions(self):
        """Only Board/Admin can update/delete"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsBoardOrAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        """Get current user's donations"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        donations = Donation.objects.filter(user=request.user).order_by('-donated_at')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get donation statistics (Board/Admin only)"""
        if not request.user.is_authenticated or request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view donation statistics'},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Sum, Count, Avg

        stats = Donation.objects.aggregate(
            total_amount=Sum('amount'),
            total_donations=Count('id'),
            average_donation=Avg('amount'),
            anonymous_donations=Count('id', filter=models.Q(is_anonymous=True))
        )

        return Response(stats)
