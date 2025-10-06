from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from assistance.models import AssistanceCase
from .models import MembershipFee, DonationRequest, VoluntaryDonation
from .serializers import (
    MembershipFeeSerializer,
    MembershipFeeUpdateSerializer,
    DonationRequestSerializer,
    VoluntaryDonationSerializer
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

    @action(detail=False, methods=['get'])
    def my_fees(self, request):
        """Get current user's fees"""
        fees = MembershipFee.objects.filter(user=request.user).order_by('-competency_month')
        serializer = self.get_serializer(fees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending fees (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view all pending fees'},
                status=status.HTTP_403_FORBIDDEN
            )

        pending_fees = MembershipFee.objects.filter(
            status='pending'
        ).select_related('user').order_by('-due_date')

        serializer = self.get_serializer(pending_fees, many=True)
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


class VoluntaryDonationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for voluntary donations (TO ORBE).

    Members: Create their own donations
    Board/Admin: View all, verify donations
    """
    queryset = VoluntaryDonation.objects.all().order_by('-donated_at')
    serializer_class = VoluntaryDonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user

        # Board/Admin see all donations
        if user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return VoluntaryDonation.objects.all().select_related('donor', 'verified_by')

        # Members see only their own (non-anonymous)
        return VoluntaryDonation.objects.filter(donor=user, is_anonymous=False)

    def perform_create(self, serializer):
        """Set donor as current user if not anonymous"""
        is_anonymous = serializer.validated_data.get('is_anonymous', False)
        if not is_anonymous:
            serializer.save(donor=self.request.user)
        else:
            serializer.save(donor=None)

    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        """Get current user's donations"""
        donations = VoluntaryDonation.objects.filter(
            donor=request.user
        ).order_by('-donated_at')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_verification(self, request):
        """Get donations pending verification (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD']:
            return Response(
                {'error': 'Only Board/Admin can view pending verifications'},
                status=status.HTTP_403_FORBIDDEN
            )

        donations = VoluntaryDonation.objects.filter(
            verified_by__isnull=True
        ).select_related('donor')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def verify(self, request, pk=None):
        """Verify a donation"""
        donation = self.get_object()

        if donation.is_verified:
            return Response(
                {'error': 'Donation already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation.verified_by = request.user
        donation.verified_at = timezone.now()
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)


class DonationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for donation requests (FOR THIRD PARTIES).

    Members: Create/Update/Delete their own pending requests
    Board/Admin: Approve/Reject requests (creates AssistanceCase when approved)
    """
    queryset = DonationRequest.objects.all().order_by('-created_at')
    serializer_class = DonationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user

        # Board/Admin see all requests
        if user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return DonationRequest.objects.all().select_related('requested_by', 'reviewed_by')

        # Members see only their own requests
        return DonationRequest.objects.filter(requested_by=user)

    def perform_create(self, serializer):
        """Set requester as current user"""
        serializer.save(requested_by=self.request.user)

    def perform_update(self, serializer):
        """Only allow members to update their own pending requests"""
        donation_request = self.get_object()
        user = self.request.user

        # Members can only edit their own pending requests
        if user.role == 'MEMBER':
            if donation_request.requested_by != user:
                raise PermissionError("You can only edit your own donation requests")
            if not donation_request.can_edit:
                raise PermissionError("You can only edit pending donation requests")

        serializer.save()

    def perform_destroy(self, instance):
        """Only allow members to delete their own pending requests"""
        user = self.request.user

        # Members can only delete their own pending requests
        if user.role == 'MEMBER':
            if instance.requested_by != user:
                raise PermissionError("You can only delete your own donation requests")
            if not instance.can_delete:
                raise PermissionError("You can only delete pending donation requests")

        instance.delete()

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's donation requests"""
        requests_qs = DonationRequest.objects.filter(
            requested_by=request.user
        ).order_by('-created_at')
        serializer = self.get_serializer(requests_qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get requests pending approval (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view pending approvals'},
                status=status.HTTP_403_FORBIDDEN
            )

        requests_qs = DonationRequest.objects.filter(
            status='pending_approval'
        ).select_related('requested_by').order_by('-created_at')
        serializer = self.get_serializer(requests_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def approve(self, request, pk=None):
        """Approve a donation request and rely on workflow automation."""
        donation_request = self.get_object()

        if donation_request.status != 'pending_approval':
            return Response(
                {'error': 'Only pending requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation_request.status = 'approved'
        donation_request.reviewed_by = request.user
        donation_request.approved_at = timezone.now()
        donation_request.save()

        serializer = self.get_serializer(donation_request)

        assistance_case_id = None
        try:
            donation_request.refresh_from_db()
            assistance_case_id = donation_request.assistance_case.id
        except AssistanceCase.DoesNotExist:
            pass

        return Response({
            **serializer.data,
            'message': 'Donation request approved successfully.',
            'assistance_case_id': assistance_case_id,
        })

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def reject(self, request, pk=None):
        """Reject a donation request"""
        donation_request = self.get_object()

        if donation_request.status != 'pending_approval':
            return Response(
                {'error': 'Only pending requests can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rejection_reason = request.data.get('rejection_reason', '')
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation_request.status = 'rejected'
        donation_request.reviewed_by = request.user
        donation_request.rejection_reason = rejection_reason
        donation_request.save()

        serializer = self.get_serializer(donation_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get donation request statistics (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view statistics'},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Sum, Count

        stats = DonationRequest.objects.aggregate(
            total_amount=Sum('amount'),
            total_requests=Count('id'),
            pending=Count('id', filter=models.Q(status='pending_approval')),
            approved=Count('id', filter=models.Q(status='approved')),
            rejected=Count('id', filter=models.Q(status='rejected'))
        )

        return Response(stats)
