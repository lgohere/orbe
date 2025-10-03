from rest_framework import serializers
from .models import MembershipFee, DonationRequest, VoluntaryDonation
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


class VoluntaryDonationSerializer(serializers.ModelSerializer):
    """Serializer for Voluntary Donations (TO ORBE)"""
    donor_name = serializers.SerializerMethodField()
    donor_email = serializers.EmailField(source='donor.email', read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = VoluntaryDonation
        fields = [
            'id',
            'donor',
            'donor_name',
            'donor_email',
            'amount',
            'message',
            'is_anonymous',
            'payment_proof',
            'donated_at',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'display_name',
            'is_verified',
        ]
        read_only_fields = [
            'id', 'donor', 'donor_name', 'donor_email', 'donated_at',
            'verified_by', 'verified_by_name', 'verified_at', 'display_name', 'is_verified'
        ]

    def get_donor_name(self, obj):
        """Get donor full name (respecting anonymity)"""
        if obj.is_anonymous or not obj.donor:
            return 'Anônimo'
        return f"{obj.donor.first_name} {obj.donor.last_name}".strip() or obj.donor.email

    def get_verified_by_name(self, obj):
        """Get verifier full name"""
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}".strip() or obj.verified_by.email
        return ''


class DonationRequestSerializer(serializers.ModelSerializer):
    """Serializer for Donation Requests (FOR THIRD PARTIES)"""
    requester_name = serializers.SerializerMethodField()
    requester_email = serializers.EmailField(source='requested_by.email', read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    can_edit = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)

    class Meta:
        model = DonationRequest
        fields = [
            'id',
            'requested_by',
            'requester_name',
            'requester_email',
            'recipient_name',
            'recipient_description',
            'amount',
            'reason',
            'urgency_level',
            'urgency_display',
            'status',
            'status_display',
            'reviewed_by',
            'reviewed_by_name',
            'rejection_reason',
            'created_at',
            'approved_at',
            'updated_at',
            'can_edit',
            'can_delete',
        ]
        read_only_fields = [
            'id', 'requested_by', 'requester_name', 'requester_email',
            'status', 'status_display', 'reviewed_by', 'reviewed_by_name',
            'rejection_reason', 'created_at', 'approved_at', 'updated_at',
            'can_edit', 'can_delete'
        ]

    def get_requester_name(self, obj):
        """Get requester full name"""
        return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip() or obj.requested_by.email

    def get_reviewed_by_name(self, obj):
        """Get reviewer full name"""
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.email
        return ''

    def validate_amount(self, value):
        """Validate amount is at least R$10"""
        if value < 10:
            raise serializers.ValidationError("Valor mínimo: R$10,00")
        return value