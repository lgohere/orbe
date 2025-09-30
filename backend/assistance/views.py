"""
Views for the assistance module.

Implements REST API endpoints for assistance cases and attachments,
including approval workflow and file uploads.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import AssistanceCase, Attachment
from .serializers import (
    AssistanceCaseListSerializer,
    AssistanceCaseDetailSerializer,
    AssistanceCaseCreateSerializer,
    AttachmentSerializer,
    CaseApprovalSerializer,
    CaseRejectionSerializer
)
from .permissions import CanCreateCase, CanApproveCase, CanEditCase


class AssistanceCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for assistance cases.

    Provides CRUD operations with role-based filtering and permissions.

    Endpoints:
    - GET /api/assistance/cases/ - List cases (role-filtered)
    - POST /api/assistance/cases/ - Create case (Board only)
    - GET /api/assistance/cases/{id}/ - Get case detail
    - PUT/PATCH /api/assistance/cases/{id}/ - Update case (creator only, if editable)
    - DELETE /api/assistance/cases/{id}/ - Delete case (Admin only)
    - POST /api/assistance/cases/{id}/approve/ - Approve case (Fiscal Council)
    - POST /api/assistance/cases/{id}/reject/ - Reject case (Fiscal Council)
    - POST /api/assistance/cases/{id}/submit/ - Submit draft for approval
    """

    queryset = AssistanceCase.objects.all().select_related(
        'created_by', 'reviewed_by'
    ).prefetch_related('attachments')

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by']
    search_fields = ['title', 'public_description']
    ordering_fields = ['created_at', 'updated_at', 'total_value']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AssistanceCaseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssistanceCaseCreateSerializer
        elif self.action == 'approve':
            return CaseApprovalSerializer
        elif self.action == 'reject':
            return CaseRejectionSerializer
        return AssistanceCaseDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [IsAuthenticated(), CanCreateCase()]
        elif self.action in ['approve', 'reject']:
            return [IsAuthenticated(), CanApproveCase()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanEditCase()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on user role.

        - Members: Only approved cases
        - Board: Their own cases + approved cases
        - Fiscal Council: Pending cases + approved cases
        - Admin: All cases
        """
        user = self.request.user

        # Admin sees everything
        if user.role == 'SUPER_ADMIN':
            return self.queryset

        # Fiscal Council sees pending + approved
        if user.role == 'FISCAL_COUNCIL':
            return self.queryset.filter(
                Q(status='pending_approval') | Q(status='approved')
            )

        # Board sees their own + approved
        if user.role == 'BOARD':
            return self.queryset.filter(
                Q(created_by=user) | Q(status='approved')
            )

        # Regular members see only approved
        return self.queryset.filter(status='approved')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveCase])
    def approve(self, request, pk=None):
        """
        Approve a pending assistance case.

        Only Fiscal Council and Admin can approve cases.

        Request: POST /api/assistance/cases/{id}/approve/
        Response: Updated case data
        """
        case = self.get_object()
        serializer = CaseApprovalSerializer(case, data={}, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            # Return full case data
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveCase])
    def reject(self, request, pk=None):
        """
        Reject a pending assistance case.

        Requires rejection reason.
        Only Fiscal Council and Admin can reject cases.

        Request: POST /api/assistance/cases/{id}/reject/
        Body: { "rejection_reason": "Motivo da rejeição..." }
        Response: Updated case data
        """
        case = self.get_object()
        serializer = CaseRejectionSerializer(case, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            # Return full case data
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit draft case for approval.

        Changes status from 'draft' to 'pending_approval'.
        Only the creator can submit their own case.

        Request: POST /api/assistance/cases/{id}/submit/
        Response: Updated case data
        """
        case = self.get_object()

        # Check if user is the creator or admin
        if case.created_by != request.user and request.user.role != 'SUPER_ADMIN':
            return Response(
                {'error': 'Você não pode enviar casos criados por outros usuários.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if case is draft
        if case.status != 'draft':
            return Response(
                {'error': f'Apenas rascunhos podem ser enviados. Status atual: {case.get_status_display()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Submit case
        success = case.submit_for_approval()
        if success:
            serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {'error': 'Falha ao enviar o caso para aprovação.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def my_cases(self, request):
        """
        Get cases created by current user.

        Request: GET /api/assistance/cases/my_cases/
        Response: List of cases
        """
        cases = self.queryset.filter(created_by=request.user)
        page = self.paginate_queryset(cases)

        if page is not None:
            serializer = AssistanceCaseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = AssistanceCaseListSerializer(cases, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, CanApproveCase])
    def pending(self, request):
        """
        Get pending cases for approval.

        Only Fiscal Council and Admin can access.

        Request: GET /api/assistance/cases/pending/
        Response: List of pending cases
        """
        cases = self.queryset.filter(status='pending_approval')
        page = self.paginate_queryset(cases)

        if page is not None:
            serializer = AssistanceCaseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = AssistanceCaseListSerializer(cases, many=True, context={'request': request})
        return Response(serializer.data)


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for case attachments.

    Provides file upload and management for assistance cases.

    Endpoints:
    - GET /api/assistance/attachments/ - List attachments (filtered by case)
    - POST /api/assistance/attachments/ - Upload attachment
    - GET /api/assistance/attachments/{id}/ - Get attachment detail
    - DELETE /api/assistance/attachments/{id}/ - Delete attachment (creator only)
    """

    queryset = Attachment.objects.all().select_related('case', 'uploaded_by')
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['case']

    def get_queryset(self):
        """
        Filter attachments based on case visibility.
        Users can only see attachments for cases they have access to.
        """
        user = self.request.user

        # Admin sees all attachments
        if user.role == 'SUPER_ADMIN':
            return self.queryset

        # Filter based on visible cases
        # Get case IDs user has access to
        if user.role == 'FISCAL_COUNCIL':
            visible_case_ids = AssistanceCase.objects.filter(
                Q(status='pending_approval') | Q(status='approved')
            ).values_list('id', flat=True)
        elif user.role == 'BOARD':
            visible_case_ids = AssistanceCase.objects.filter(
                Q(created_by=user) | Q(status='approved')
            ).values_list('id', flat=True)
        else:
            # Regular members see only approved case attachments
            visible_case_ids = AssistanceCase.objects.filter(
                status='approved'
            ).values_list('id', flat=True)

        return self.queryset.filter(case_id__in=visible_case_ids)

    def perform_create(self, serializer):
        """
        Validate case access before allowing upload.
        Users can only upload to cases they can edit.
        """
        case = serializer.validated_data.get('case')

        # Check if user has permission to upload to this case
        user = self.request.user

        # Admin can always upload
        if user.role == 'SUPER_ADMIN':
            serializer.save(uploaded_by=user)
            return

        # Board member can upload to their own cases (if editable)
        if case.created_by == user and case.can_be_edited:
            serializer.save(uploaded_by=user)
            return

        # Fiscal Council can upload supporting documents to pending cases
        if user.role == 'FISCAL_COUNCIL' and case.status == 'pending_approval':
            serializer.save(uploaded_by=user)
            return

        # Otherwise, deny
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Você não tem permissão para adicionar anexos a este caso.")

    def perform_destroy(self, instance):
        """
        Allow deletion only by uploader, case creator, or admin.
        Cannot delete from approved cases.
        """
        user = self.request.user

        # Admin can always delete
        if user.role == 'SUPER_ADMIN':
            instance.delete()
            return

        # Can't delete from approved cases
        if instance.case.status == 'approved':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Não é possível remover anexos de casos aprovados.")

        # Uploader can delete their own uploads
        if instance.uploaded_by == user:
            instance.delete()
            return

        # Case creator can delete attachments from their case
        if instance.case.created_by == user:
            instance.delete()
            return

        # Otherwise, deny
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Você não tem permissão para remover este anexo.")
