"""
Serializers for the assistance module.

Handles serialization/deserialization of assistance cases and attachments
for the REST API, including role-based field visibility.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AssistanceCase, Attachment

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
    Includes internal_description (with permission check) and attachments.
    """
    created_by = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
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
            'rejection_reason',
            'attachments',
            'attachment_count',
            'can_be_edited',
            'is_draft',
            'is_pending',
            'is_approved',
            'is_rejected'
        ]
        read_only_fields = [
            'id', 'status', 'created_at', 'updated_at', 'approved_at',
            'created_by', 'reviewed_by', 'rejection_reason'
        ]

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
