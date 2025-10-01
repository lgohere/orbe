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
    ViewSet for donation requests.

    Members: Create/Update/Delete their own pending requests
    Board/Admin: Approve, Attach Proof, Complete all requests
    """
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializer for creation"""
        if self.action == 'create':
            return DonationCreateSerializer
        return DonationSerializer

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user

        # Board/Admin see all donation requests
        if user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Donation.objects.all().select_related('user', 'reviewed_by')

        # Members see only their own requests
        return Donation.objects.filter(user=user)

    def perform_create(self, serializer):
        """Set requester as current user"""
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """Members can only edit/delete their own pending requests"""
        if self.action in ['update', 'partial_update', 'destroy']:
            # Custom permission check in perform_update/destroy
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_update(self, serializer):
        """Only allow members to update their own pending requests"""
        donation = self.get_object()
        user = self.request.user

        # Members can only edit their own pending requests
        if user.role == 'MEMBER':
            if donation.user != user:
                raise PermissionError("You can only edit your own donation requests")
            if not donation.can_edit:
                raise PermissionError("You can only edit pending donation requests")

        serializer.save()

    def perform_destroy(self, instance):
        """Only allow members to delete their own pending requests"""
        user = self.request.user

        # Members can only delete their own pending requests
        if user.role == 'MEMBER':
            if instance.user != user:
                raise PermissionError("You can only delete your own donation requests")
            if not instance.can_delete:
                raise PermissionError("You can only delete pending donation requests")

        instance.delete()

    @action(detail=False, methods=['get'])
    def my_donations(self, request):
        """Get current user's donation requests"""
        donations = Donation.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get donations pending approval (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view pending approvals'},
                status=status.HTTP_403_FORBIDDEN
            )

        donations = Donation.objects.filter(status='pending_approval').select_related('user')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_proof(self, request):
        """Get approved donations pending proof attachment (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD']:
            return Response(
                {'error': 'Only Board/Admin can view this'},
                status=status.HTTP_403_FORBIDDEN
            )

        donations = Donation.objects.filter(status='approved').select_related('user')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed donations"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view completed donations'},
                status=status.HTTP_403_FORBIDDEN
            )

        donations = Donation.objects.filter(status='completed').select_related('user', 'reviewed_by')
        serializer = self.get_serializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def approve(self, request, pk=None):
        """Approve a donation request"""
        donation = self.get_object()

        if donation.status != 'pending_approval':
            return Response(
                {'error': 'Only pending requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation.status = 'approved'
        donation.reviewed_by = request.user
        donation.approved_at = timezone.now()
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def reject(self, request, pk=None):
        """Reject a donation request"""
        donation = self.get_object()

        if donation.status != 'pending_approval':
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

        donation.status = 'rejected'
        donation.reviewed_by = request.user
        donation.rejection_reason = rejection_reason
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def attach_proof(self, request, pk=None):
        """Attach proof document to approved donation"""
        donation = self.get_object()

        if donation.status != 'approved':
            return Response(
                {'error': 'Only approved donations can have proof attached'},
                status=status.HTTP_400_BAD_REQUEST
            )

        proof_file = request.FILES.get('proof_document')
        if not proof_file:
            return Response(
                {'error': 'Proof document file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation.proof_document = proof_file
        donation.status = 'proof_attached'
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def complete(self, request, pk=None):
        """Mark donation as completed"""
        donation = self.get_object()

        if donation.status not in ['approved', 'proof_attached']:
            return Response(
                {'error': 'Only approved/proof-attached donations can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        donation.status = 'completed'
        donation.completed_at = timezone.now()
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    # ========== REGRESSÃO DE ETAPAS ==========

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def unapprove(self, request, pk=None):
        """Revert donation from approved/proof_attached back to pending_approval"""
        donation = self.get_object()

        if donation.status not in ['approved', 'proof_attached']:
            return Response(
                {'error': 'Only approved or proof-attached donations can be unapproved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Revert to pending approval
        donation.status = 'pending_approval'
        donation.reviewed_by = None
        donation.approved_at = None
        donation.proof_document = None  # Remove proof if exists
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def remove_proof(self, request, pk=None):
        """Remove proof document and revert to approved status"""
        donation = self.get_object()

        if donation.status not in ['proof_attached', 'completed']:
            return Response(
                {'error': 'Only proof-attached or completed donations can have proof removed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove proof and revert to approved
        donation.proof_document = None
        donation.status = 'approved'
        donation.completed_at = None  # Clear completion date if was completed
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsBoardOrAdmin])
    def reopen(self, request, pk=None):
        """Reopen a completed or rejected donation back to pending approval"""
        donation = self.get_object()

        if donation.status not in ['completed', 'rejected']:
            return Response(
                {'error': 'Only completed or rejected donations can be reopened'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset to pending approval
        donation.status = 'pending_approval'
        donation.reviewed_by = None
        donation.approved_at = None
        donation.completed_at = None
        donation.rejection_reason = ''
        donation.proof_document = None
        donation.save()

        serializer = self.get_serializer(donation)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get donation statistics (Board/Admin only)"""
        if request.user.role not in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return Response(
                {'error': 'Only Board/Admin can view statistics'},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.db.models import Sum, Count

        stats = Donation.objects.aggregate(
            total_amount=Sum('amount'),
            total_requests=Count('id'),
            pending=Count('id', filter=models.Q(status='pending_approval')),
            approved=Count('id', filter=models.Q(status='approved')),
            completed=Count('id', filter=models.Q(status='completed')),
            rejected=Count('id', filter=models.Q(status='rejected'))
        )

        return Response(stats)
