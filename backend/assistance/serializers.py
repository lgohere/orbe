"""
Serializers for the assistance module.

Handles serialization/deserialization of assistance cases and attachments
for the REST API, including role-based field visibility.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AssistanceCase, Attachment, CaseTimeline

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role']
        read_only_fields = fields

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for case attachments"""
    uploaded_by = UserBasicSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_pdf = serializers.ReadOnlyField()
    file_icon = serializers.ReadOnlyField()

    class Meta:
        model = Attachment
        fields = [
            'id',
            'case',
            'attachment_type',
            'file',
            'file_url',
            'file_name',
            'file_type',
            'file_size',
            'file_size_mb',
            'is_image',
            'is_pdf',
            'file_icon',
            'uploaded_at',
            'uploaded_by'
        ]
        read_only_fields = ['id', 'file_name', 'file_type', 'file_size', 'uploaded_at', 'uploaded_by']

    def get_file_url(self, obj):
        """Get absolute URL for file"""
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def create(self, validated_data):
        """Set uploaded_by from request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class AssistanceCaseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for case lists.
    Excludes internal_description to reduce payload size.
    """
    created_by = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    attachment_count = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_edited = serializers.ReadOnlyField()

    class Meta:
        model = AssistanceCase
        fields = [
            'id',
            'title',
            'public_description',
            'total_value',
            'status',
            'status_display',
            'created_by',
            'reviewed_by',
            'created_at',
            'updated_at',
            'approved_at',
            'attachment_count',
            'can_be_edited'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'approved_at', 'created_by', 'reviewed_by']


class AssistanceCaseDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for case details.
    Includes internal_description (with permission check), attachments, and timeline.
    """
    created_by = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    timeline_events = serializers.SerializerMethodField()
    attachment_count = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_be_edited = serializers.ReadOnlyField()
    is_draft = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    is_rejected = serializers.ReadOnlyField()

    class Meta:
        model = AssistanceCase
        fields = [
            'id',
            'title',
            'public_description',
            'internal_description',
            'total_value',
            'status',
            'status_display',
            'created_by',
            'reviewed_by',
            'created_at',
            'updated_at',
            'approved_at',
            'bank_info_submitted_at',
            'transfer_confirmed_at',
            'member_proof_submitted_at',
            'completed_at',
            'beneficiary_name',
            'beneficiary_cpf',
            'beneficiary_bank',
            'beneficiary_account_type',
            'beneficiary_agency',
            'beneficiary_account',
            'beneficiary_pix_key',
            'rejection_reason',
            'attachments',
            'timeline_events',
            'attachment_count',
            'can_be_edited',
            'is_draft',
            'is_pending',
            'is_approved',
            'is_rejected',
            'is_awaiting_bank_info',
            'is_awaiting_transfer',
            'is_awaiting_member_proof',
            'is_pending_validation'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 'approved_at',
            'bank_info_submitted_at', 'transfer_confirmed_at', 'member_proof_submitted_at', 'completed_at',
            'created_by', 'reviewed_by', 'rejection_reason',
            'beneficiary_name', 'beneficiary_cpf', 'beneficiary_bank',
            'beneficiary_account_type', 'beneficiary_agency', 'beneficiary_account',
            'beneficiary_pix_key'
        ]

    def get_timeline_events(self, obj):
        """Get timeline events for this case"""
        # Import here to avoid circular import
        events = obj.timeline_events.all()
        return CaseTimelineSerializer(events, many=True, context=self.context).data

    def to_representation(self, instance):
        """
        Hide internal_description from regular members.
        Only Board, Fiscal Council, and Admin can see internal notes.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Check if user has permission to see internal description
        if request and hasattr(request, 'user'):
            user = request.user
            # Only Board, Fiscal Council, and Admin see internal description
            if user.role not in ['BOARD', 'FISCAL_COUNCIL', 'SUPER_ADMIN']:
                data.pop('internal_description', None)

        return data


class AssistanceCaseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating assistance cases.
    Validates business rules and sets creator.
    """

    class Meta:
        model = AssistanceCase
        fields = [
            'id',
            'title',
            'public_description',
            'internal_description',
            'total_value',
            'status'
        ]
        read_only_fields = ['id']

    def validate_total_value(self, value):
        """Ensure total value is positive"""
        if value <= 0:
            raise serializers.ValidationError("O valor total deve ser maior que zero.")
        return value

    def validate_title(self, value):
        """Ensure title is not too short"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("O título deve ter pelo menos 10 caracteres.")
        return value

    def validate_public_description(self, value):
        """Ensure public description is adequate"""
        if len(value.strip()) < 50:
            raise serializers.ValidationError("A descrição pública deve ter pelo menos 50 caracteres.")
        return value

    def validate_internal_description(self, value):
        """Ensure internal description is adequate"""
        if len(value.strip()) < 30:
            raise serializers.ValidationError("A descrição interna deve ter pelo menos 30 caracteres.")
        return value

    def validate_status(self, value):
        """
        Validate status transitions.
        Only allow draft or pending_approval on create/update.
        Approval/rejection handled by separate endpoints.
        """
        if value not in ['draft', 'pending_approval']:
            raise serializers.ValidationError(
                "Apenas os status 'draft' e 'pending_approval' podem ser definidos diretamente. "
                "Use os endpoints de aprovação/rejeição."
            )
        return value

    def create(self, validated_data):
        """Set created_by from request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Validate edit permissions.
        Only drafts and rejected cases can be edited.
        """
        if not instance.can_be_edited:
            raise serializers.ValidationError({
                'non_field_errors': [
                    f"Casos com status '{instance.get_status_display()}' não podem ser editados. "
                    "Apenas rascunhos e casos rejeitados podem ser modificados."
                ]
            })

        return super().update(instance, validated_data)


class CaseApprovalSerializer(serializers.Serializer):
    """
    Serializer for case approval action.
    Used by Fiscal Council to approve pending cases.
    """
    # No additional fields needed - approval is just an action

    def validate(self, attrs):
        """Ensure case is in pending status"""
        case = self.instance
        if case.status != 'pending_approval':
            raise serializers.ValidationError(
                f"Apenas casos pendentes podem ser aprovados. Status atual: {case.get_status_display()}"
            )
        return attrs

    def save(self):
        """Approve the case"""
        request = self.context.get('request')
        case = self.instance
        success = case.approve(reviewer_user=request.user)
        if not success:
            raise serializers.ValidationError("Falha ao aprovar o caso.")
        return case


class CaseRejectionSerializer(serializers.Serializer):
    """
    Serializer for case rejection action.
    Requires rejection reason from Fiscal Council.
    """
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        min_length=20,
        max_length=1000,
        help_text="Motivo da rejeição (mínimo 20 caracteres)"
    )

    def validate(self, attrs):
        """Ensure case is in pending status"""
        case = self.instance
        if case.status != 'pending_approval':
            raise serializers.ValidationError(
                f"Apenas casos pendentes podem ser rejeitados. Status atual: {case.get_status_display()}"
            )
        return attrs

    def validate_rejection_reason(self, value):
        """Ensure rejection reason is meaningful"""
        if len(value.strip()) < 20:
            raise serializers.ValidationError("O motivo da rejeição deve ter pelo menos 20 caracteres.")
        return value

    def save(self):
        """Reject the case with reason"""
        request = self.context.get('request')
        case = self.instance
        reason = self.validated_data['rejection_reason']
        success = case.reject(reviewer_user=request.user, reason=reason)
        if not success:
            raise serializers.ValidationError("Falha ao rejeitar o caso.")
        return case


class ConfirmTransferSerializer(serializers.Serializer):
    """
    Serializer for admin confirming transfer to member.
    STEP 2: Admin uploads PIX/transfer receipt.
    """
    # No additional fields - admin must upload attachment separately

    def validate(self, attrs):
        """Ensure case is awaiting transfer and has payment proof"""
        case = self.instance
        if case.status != 'awaiting_transfer':
            raise serializers.ValidationError(
                f"Apenas casos aguardando transferência podem ser confirmados. "
                f"Status atual: {case.get_status_display()}"
            )

        # Check if payment proof was uploaded
        payment_proofs = case.attachments.filter(attachment_type='payment_proof')
        if not payment_proofs.exists():
            raise serializers.ValidationError(
                "É necessário enviar o comprovante de transferência (PIX ou transferência bancária) "
                "antes de confirmar a transferência."
            )

        return attrs

    def save(self):
        """Confirm transfer"""
        request = self.context.get('request')
        case = self.instance
        success = case.confirm_transfer(admin_user=request.user)
        if not success:
            raise serializers.ValidationError("Falha ao confirmar transferência.")
        return case


class SubmitMemberProofSerializer(serializers.Serializer):
    """
    Serializer for member submitting application proof.
    STEP 3: Member uploads photos + receipts showing donation was applied.
    """
    # No additional fields - member must upload attachments separately

    def validate(self, attrs):
        """Ensure case is awaiting member proof"""
        case = self.instance
        if case.status != 'awaiting_member_proof':
            raise serializers.ValidationError(
                f"Apenas casos aguardando comprovação do membro podem receber comprovantes. "
                f"Status atual: {case.get_status_display()}"
            )

        # Ensure user is the creator (member who requested)
        request = self.context.get('request')
        if case.created_by != request.user:
            raise serializers.ValidationError(
                "Apenas o membro que solicitou pode enviar comprovantes."
            )

        return attrs

    def save(self):
        """Submit member proof"""
        case = self.instance
        success = case.submit_member_proof()
        if not success:
            raise serializers.ValidationError("Falha ao enviar comprovantes.")
        return case


class CompleteCaseSerializer(serializers.Serializer):
    """
    Serializer for admin completing and validating case.
    STEP 4: Admin reviews all attachments and marks as completed.
    """
    # No additional fields needed

    def validate(self, attrs):
        """Ensure case is pending validation"""
        case = self.instance
        if case.status != 'pending_validation':
            raise serializers.ValidationError(
                f"Apenas casos pendentes de validação podem ser concluídos. "
                f"Status atual: {case.get_status_display()}"
            )

        # Ensure case has required attachments
        transfer_proofs = case.attachments.filter(attachment_type='payment_proof').count()
        member_proofs = case.attachments.filter(attachment_type='photo_evidence').count()

        if transfer_proofs == 0:
            raise serializers.ValidationError(
                "O caso deve ter pelo menos um comprovante de transferência do admin."
            )

        if member_proofs == 0:
            raise serializers.ValidationError(
                "O caso deve ter pelo menos uma foto/comprovante do membro."
            )

        return attrs

    def save(self):
        """Complete and validate case"""
        request = self.context.get('request')
        case = self.instance
        success = case.complete(reviewer_user=request.user)
        if not success:
            raise serializers.ValidationError("Falha ao concluir o caso.")
        return case


class BankInfoSerializer(serializers.Serializer):
    """Member submits beneficiary bank information after approval"""
    beneficiary_name = serializers.CharField(
        max_length=200,
        required=True,
        help_text='Nome completo do beneficiário'
    )
    beneficiary_cpf = serializers.CharField(
        max_length=14,
        required=True,
        help_text='CPF no formato 000.000.000-00'
    )
    beneficiary_bank = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text='Nome do banco (opcional se tiver PIX)'
    )
    beneficiary_account_type = serializers.ChoiceField(
        choices=[
            ('corrente', 'Conta Corrente'),
            ('poupanca', 'Conta Poupança'),
            ('pagamento', 'Conta Pagamento')
        ],
        required=False,
        allow_blank=True
    )
    beneficiary_agency = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True,
        help_text='Número da agência'
    )
    beneficiary_account = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text='Número da conta com dígito'
    )
    beneficiary_pix_key = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text='Chave PIX (CPF, e-mail, telefone ou chave aleatória)'
    )

    def validate(self, attrs):
        case = self.instance

        # Check status
        if case.status != 'awaiting_bank_info':
            raise serializers.ValidationError(
                f"Apenas casos aguardando dados bancários podem receber informações. "
                f"Status atual: {case.get_status_display()}"
            )

        # Ensure user is the creator
        request = self.context.get('request')
        if case.created_by != request.user:
            raise serializers.ValidationError(
                "Apenas o membro que solicitou pode informar dados bancários."
            )

        # Validate CPF format (basic)
        cpf = attrs.get('beneficiary_cpf', '')
        if cpf and not self._validate_cpf_format(cpf):
            raise serializers.ValidationError({
                'beneficiary_cpf': 'CPF deve estar no formato 000.000.000-00'
            })

        # Require either full bank info OR PIX key
        has_bank_info = all([
            attrs.get('beneficiary_bank'),
            attrs.get('beneficiary_agency'),
            attrs.get('beneficiary_account')
        ])
        has_pix = attrs.get('beneficiary_pix_key')

        if not has_bank_info and not has_pix:
            raise serializers.ValidationError(
                "É necessário informar dados bancários completos (banco, agência, conta) "
                "OU uma chave PIX."
            )

        return attrs

    def _validate_cpf_format(self, cpf):
        """Basic CPF format validation (000.000.000-00)"""
        import re
        # Allow with or without formatting
        cpf_clean = re.sub(r'[^\d]', '', cpf)
        return len(cpf_clean) == 11

    def save(self):
        case = self.instance
        success = case.submit_bank_info(self.validated_data)
        if not success:
            raise serializers.ValidationError("Falha ao submeter dados bancários.")
        return case


class CaseTimelineSerializer(serializers.ModelSerializer):
    """
    Serializer for case timeline events.
    Provides complete history of all actions on a case.
    """
    user_name = serializers.SerializerMethodField()
    event_display = serializers.CharField(source='get_event_type_display', read_only=True)
    event_icon = serializers.SerializerMethodField()
    event_color = serializers.SerializerMethodField()

    class Meta:
        model = CaseTimeline
        fields = [
            'id',
            'event_type',
            'event_display',
            'event_icon',
            'event_color',
            'description',
            'user_name',
            'metadata',
            'created_at'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        """Get full name of user who performed action"""
        if obj.user:
            return obj.user.get_full_name()
        return 'Sistema'

    def get_event_icon(self, obj):
        """Get Material Design icon for each event type"""
        icon_map = {
            'case_created': 'mdi-plus-circle',
            'submitted_for_approval': 'mdi-send',
            'approved': 'mdi-check-circle',
            'rejected': 'mdi-close-circle',
            'bank_info_submitted': 'mdi-bank',
            'transfer_confirmed': 'mdi-cash-check',
            'member_proof_submitted': 'mdi-file-upload',
            'completed': 'mdi-check-all',
            'attachment_uploaded': 'mdi-paperclip',
            'status_changed': 'mdi-update',
            'comment_added': 'mdi-comment-text',
        }
        return icon_map.get(obj.event_type, 'mdi-circle-small')

    def get_event_color(self, obj):
        """Get color for each event type (for UI)"""
        color_map = {
            'case_created': 'primary',
            'submitted_for_approval': 'info',
            'approved': 'success',
            'rejected': 'error',
            'bank_info_submitted': 'info',
            'transfer_confirmed': 'success',
            'member_proof_submitted': 'info',
            'completed': 'success',
            'attachment_uploaded': 'grey',
            'status_changed': 'warning',
            'comment_added': 'grey',
        }
        return color_map.get(obj.event_type, 'grey')
