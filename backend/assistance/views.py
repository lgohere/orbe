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
import django_filters

from .models import AssistanceCase, Attachment
from .serializers import (
    AssistanceCaseListSerializer,
    AssistanceCaseDetailSerializer,
    AssistanceCaseCreateSerializer,
    AttachmentSerializer,
    CaseApprovalSerializer,
    CaseRejectionSerializer,
    BankInfoSerializer,
    ConfirmTransferSerializer,
    SubmitMemberProofSerializer,
    CompleteCaseSerializer,
    DirectDonationSerializer
)
from .permissions import CanCreateCase, CanApproveCase, CanEditCase


class AssistanceCaseFilter(django_filters.FilterSet):
    """Custom filter for AssistanceCase to support exclude_status"""
    exclude_status = django_filters.CharFilter(field_name='status', exclude=True)

    class Meta:
        model = AssistanceCase
        fields = ['status', 'created_by', 'exclude_status']


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
    filterset_class = AssistanceCaseFilter
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

        - Members: Own cases + completed cases
        - Board: Their own cases + completed cases
        - Fiscal Council: All cases (need to approve/validate)
        - Admin: All cases
        """
        user = self.request.user

        # Admin sees everything
        if user.role == 'SUPER_ADMIN':
            return self.queryset

        # Fiscal Council sees everything (need to approve/validate)
        if user.role == 'FISCAL_COUNCIL':
            return self.queryset

        # Board sees their own + completed
        if user.role == 'BOARD':
            return self.queryset.filter(
                Q(created_by=user) | Q(status='completed')
            )

        # Regular members see their own cases + completed cases
        return self.queryset.filter(
            Q(created_by=user) | Q(status='completed')
        )

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

    @action(detail=True, methods=['post'])
    def submit_bank_info(self, request, pk=None):
        """
        STEP 1.5: Member provides beneficiary bank information after approval.
        Required before admin can transfer funds.

        Request: POST /api/assistance/cases/{id}/submit_bank_info/
        Body: {
            "beneficiary_name": "João Silva",
            "beneficiary_cpf": "000.000.000-00",
            "beneficiary_pix_key": "joao@email.com" (or full bank info)
        }
        Response: Updated case data
        """
        case = self.get_object()
        serializer = BankInfoSerializer(case, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response({
                'message': 'Dados bancários enviados com sucesso! Aguardando transferência do admin.',
                'case': detail_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveCase])
    def confirm_transfer(self, request, pk=None):
        """
        STEP 2: Admin confirms they transferred money to member.
        Must upload PIX/transfer receipt as attachment.

        Request: POST /api/assistance/cases/{id}/confirm_transfer/
        Response: Updated case data
        """
        case = self.get_object()
        serializer = ConfirmTransferSerializer(case, data={}, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response({
                'message': 'Transferência confirmada. Aguardando comprovação do membro.',
                'case': detail_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def submit_member_proof(self, request, pk=None):
        """
        STEP 3: Member submits proof of application to beneficiary.
        Must upload photos + receipts as attachments.

        Request: POST /api/assistance/cases/{id}/submit_member_proof/
        Response: Updated case data
        """
        case = self.get_object()
        serializer = SubmitMemberProofSerializer(case, data={}, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response({
                'message': 'Comprovantes enviados. Aguardando validação do administrador.',
                'case': detail_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanApproveCase])
    def complete(self, request, pk=None):
        """
        STEP 4: Admin validates all proofs and completes case.
        Checks that transfer proof + member proof exist.
        Marks case as completed and ready for feed publication.

        Request: POST /api/assistance/cases/{id}/complete/
        Response: Updated case data
        """
        case = self.get_object()
        serializer = CompleteCaseSerializer(case, data={}, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response({
                'message': 'Caso validado e concluído com sucesso!',
                'case': detail_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanApproveCase])
    def create_direct_donation(self, request):
        """
        Admin creates a direct donation case (bypasses member workflow).

        This is for when the admin directly assists a member:
        - No member proof submission needed
        - Case goes straight to 'completed' status
        - Admin uploads payment proof (PIX/transfer receipt)
        - Admin uploads evidence photos

        Request: POST /api/assistance/cases/create_direct_donation/
        Body: {
            "member_id": 123,
            "title": "Título do caso",
            "public_description": "Descrição pública...",
            "internal_description": "Notas internas...",
            "total_value": 500.00
        }
        Response: Created case data
        """
        serializer = DirectDonationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            case = serializer.save()
            detail_serializer = AssistanceCaseDetailSerializer(case, context={'request': request})
            return Response({
                'message': 'Doação direta criada com sucesso! Agora anexe os comprovantes.',
                'case': detail_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            # Regular members see attachments from:
            # 1. Their own cases (any status)
            # 2. Approved cases (public)
            visible_case_ids = AssistanceCase.objects.filter(
                Q(created_by=user) | Q(status='approved')
            ).values_list('id', flat=True)

        return self.queryset.filter(case_id__in=visible_case_ids)

    def perform_create(self, serializer):
        """
        Validate case access before allowing upload.
        Different permissions based on case status and attachment type.
        """
        case = serializer.validated_data.get('case')
        attachment_type = serializer.validated_data.get('attachment_type', 'other')
        user = self.request.user

        # Admin can always upload
        if user.role == 'SUPER_ADMIN':
            serializer.save(uploaded_by=user)
            return

        # Fiscal Council can upload to pending cases or awaiting transfer (payment_proof)
        if user.role == 'FISCAL_COUNCIL':
            if case.status == 'pending_approval':
                serializer.save(uploaded_by=user)
                return
            if case.status == 'awaiting_transfer' and attachment_type == 'payment_proof':
                serializer.save(uploaded_by=user)
                return

        # Member can upload to their own cases in specific statuses
        if case.created_by == user:
            # Can edit drafts and rejected cases
            if case.can_be_edited:
                serializer.save(uploaded_by=user)
                return
            # Can upload member proof when awaiting it
            if case.status == 'awaiting_member_proof' and attachment_type == 'photo_evidence':
                serializer.save(uploaded_by=user)
                return

        # Otherwise, deny
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Você não tem permissão para adicionar anexos a este caso.")

    def perform_destroy(self, instance):
        """
        Allow deletion only by uploader or admin.

        CRITICAL BUSINESS RULE:
        - Admin can delete any attachment
        - Users can ONLY delete their own uploads
        - Members CANNOT delete admin's attachments (payment_proof)
        - Cannot delete from completed cases
        """
        user = self.request.user

        # Admin can always delete
        if user.role == 'SUPER_ADMIN':
            instance.delete()
            return

        # Can't delete from completed cases
        if instance.case.status == 'completed':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Não é possível remover anexos de casos concluídos.")

        # ONLY uploader can delete their own uploads
        # This prevents members from deleting admin's payment_proof
        if instance.uploaded_by == user:
            instance.delete()
            return

        # Otherwise, deny
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Você só pode remover anexos que você mesmo enviou.")
