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
    """Serializer for Donation model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    donor_display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Donation
        fields = [
            'id',
            'user',
            'user_email',
            'donor_display_name',
            'amount',
            'message',
            'is_anonymous',
            'donated_at',
        ]
        read_only_fields = ['id', 'user_email', 'donor_display_name', 'donated_at']

    def validate(self, attrs):
        """Custom validation for donation"""
        # If user is not provided, force anonymous
        if not attrs.get('user'):
            attrs['is_anonymous'] = True
        return attrs


class DonationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating donations (simplified)"""

    class Meta:
        model = Donation
        fields = ['amount', 'message', 'is_anonymous']

    def create(self, validated_data):
        """Create donation with user from request context"""
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        validated_data['user'] = user
        return super().create(validated_data)