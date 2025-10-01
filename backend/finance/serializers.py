from rest_framework import serializers
from .models import MembershipFee, Donation
from users.serializers import UserSerializer


class MembershipFeeSerializer(serializers.ModelSerializer):
    """Serializer for MembershipFee model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    class Meta:
        model = MembershipFee
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'competency_month',
            'amount',
            'due_date',
            'status',
            'paid_at',
            'reminder_sent_at',
            'overdue_reminder_sent_at',
            'notes',
            'is_overdue',
            'days_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user_email',
            'user_name',
            'is_overdue',
            'days_overdue',
            'created_at',
            'updated_at',
        ]

    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email


class MembershipFeeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating membership fee status"""

    class Meta:
        model = MembershipFee
        fields = ['status', 'paid_at', 'notes']

    def validate_status(self, value):
        """Validate status transition"""
        if value == 'paid' and not self.instance.paid_at and not self.initial_data.get('paid_at'):
            raise serializers.ValidationError(
                "paid_at must be provided when marking fee as paid"
            )
        return value


class DonationSerializer(serializers.ModelSerializer):
    """Serializer for Donation Request model"""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)

    class Meta:
        model = Donation
        fields = [
            'id',
            'user',
            'user_name',
            'user_email',
            'recipient',
            'amount',
            'reason',
            'status',
            'status_display',
            'reviewed_by',
            'reviewed_by_name',
            'rejection_reason',
            'proof_document',
            'created_at',
            'approved_at',
            'completed_at',
            'can_edit',
            'can_delete',
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_email', 'status', 'status_display',
            'reviewed_by', 'reviewed_by_name', 'rejection_reason',
            'created_at', 'approved_at', 'completed_at', 'can_edit', 'can_delete'
        ]

    def get_user_name(self, obj):
        """Get requester full name"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
        return ''

    def get_reviewed_by_name(self, obj):
        """Get reviewer full name"""
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.email
        return ''


class DonationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating donation requests"""

    class Meta:
        model = Donation
        fields = ['recipient', 'amount', 'reason']

    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

    def validate_recipient(self, value):
        """Validate recipient is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Recipient name is required")
        return value.strip()

    def validate_reason(self, value):
        """Validate reason is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Reason is required")
        return value.strip()