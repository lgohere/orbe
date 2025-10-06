"""
Serializers for users app
"""

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from django.db import models
from .models import UserProfile
import requests
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'registration_method', 'is_active', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active', 'registration_method']


class UserAutocompleteSerializer(serializers.ModelSerializer):
    """Lightweight serializer for autocomplete/search fields"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']


class MemberListSerializer(serializers.ModelSerializer):
    """Serializer for member list with financial summary"""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    financial_summary = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'date_joined',
            'registration_method', 'profile', 'financial_summary'
        ]

    def get_financial_summary(self, obj):
        """Get financial summary for member"""
        from finance.models import MembershipFee, VoluntaryDonation
        from django.db.models import Sum, Count, Q

        # Membership fees summary
        fees = MembershipFee.objects.filter(user=obj)
        total_fees = fees.count()
        paid_fees = fees.filter(status='paid').count()
        pending_fees = fees.filter(status='pending').count()
        overdue_fees = fees.filter(status='overdue').count()
        total_fees_amount = fees.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Voluntary donations summary
        donations = VoluntaryDonation.objects.filter(donor=obj)
        total_donations = donations.count()
        total_donations_amount = donations.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Last payment date
        last_payment = fees.filter(status='paid').order_by('-paid_at').first()
        last_payment_date = last_payment.paid_at if last_payment else None

        return {
            'membership': {
                'total_fees': total_fees,
                'paid': paid_fees,
                'pending': pending_fees,
                'overdue': overdue_fees,
                'total_amount_paid': float(total_fees_amount),
                'last_payment_date': last_payment_date
            },
            'donations': {
                'total_count': total_donations,
                'total_amount': float(total_donations_amount)
            },
            'total_contributed': float(total_fees_amount + total_donations_amount)
        }


class MemberDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual member"""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    financial_summary = serializers.SerializerMethodField()
    membership_fees = serializers.SerializerMethodField()
    donations = serializers.SerializerMethodField()
    assistance_cases = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'date_joined',
            'registration_method', 'profile', 'financial_summary',
            'membership_fees', 'donations', 'assistance_cases'
        ]

    def get_financial_summary(self, obj):
        """Get complete financial summary"""
        from finance.models import MembershipFee, VoluntaryDonation
        from django.db.models import Sum

        # Membership fees
        fees = MembershipFee.objects.filter(user=obj)
        fees_paid = fees.filter(status='paid')
        total_fees_amount = fees_paid.aggregate(total=Sum('amount'))['total'] or 0

        # Donations
        donations = VoluntaryDonation.objects.filter(donor=obj)
        total_donations_amount = donations.aggregate(total=Sum('amount'))['total'] or 0

        return {
            'total_fees': fees.count(),
            'paid_fees': fees_paid.count(),
            'pending_fees': fees.filter(status='pending').count(),
            'overdue_fees': fees.filter(status='overdue').count(),
            'total_fees_amount': float(total_fees_amount),
            'total_donations': donations.count(),
            'total_donations_amount': float(total_donations_amount),
            'total_contributed': float(total_fees_amount + total_donations_amount)
        }

    def get_membership_fees(self, obj):
        """Get recent membership fees (last 12 months)"""
        from finance.models import MembershipFee
        from datetime import date, timedelta

        one_year_ago = date.today() - timedelta(days=365)
        fees = MembershipFee.objects.filter(
            user=obj,
            competency_month__gte=one_year_ago
        ).order_by('-competency_month')[:12]

        return [{
            'id': fee.id,
            'competency_month': fee.competency_month,
            'amount': float(fee.amount),
            'due_date': fee.due_date,
            'status': fee.status,
            'paid_at': fee.paid_at,
            'reminder_sent_at': fee.reminder_sent_at
        } for fee in fees]

    def get_donations(self, obj):
        """Get recent donations (last 10)"""
        from finance.models import VoluntaryDonation

        donations = VoluntaryDonation.objects.filter(donor=obj).order_by('-donated_at')[:10]

        return [{
            'id': donation.id,
            'amount': float(donation.amount) if donation.amount else None,
            'message': donation.message,
            'donated_at': donation.donated_at,
            'payment_proof': donation.payment_proof.url if donation.payment_proof else None
        } for donation in donations]

    def get_assistance_cases(self, obj):
        """Get assistance cases for member"""
        from assistance.models import AssistanceCase

        cases = AssistanceCase.objects.filter(
            models.Q(created_by=obj) | models.Q(linked_members=obj)
        ).distinct().order_by('-created_at')[:5]

        return [{
            'id': case.id,
            'title': case.title,
            'status': case.status,
            'total_value': float(case.total_value),
            'created_at': case.created_at,
            'approved_at': case.approved_at
        } for case in cases]


class CustomRegisterSerializer(RegisterSerializer):
    """Custom registration serializer"""

    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone = serializers.CharField(required=False, max_length=20)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone': self.validated_data.get('phone', ''),
        })
        return data

    def save(self, request):
        user = super().save(request)

        # Update profile with phone if provided
        if self.validated_data.get('phone'):
            user.profile.phone = self.validated_data.get('phone')
            user.profile.save()

        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""

    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address_line1', 'address_line2', 'city', 'state',
            'zip_code', 'country', 'membership_due_day', 'theme_preference',
            'language_preference'
        ]

    def validate_membership_due_day(self, value):
        """Validate membership due day is between 1 and 28"""
        if not (1 <= value <= 28):
            raise serializers.ValidationError(
                "Membership due day must be between 1 and 28"
            )
        return value


class OnboardingSerializer(serializers.Serializer):
    """Serializer for onboarding process"""

    # Step 1: Personal info
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)

    # Step 2: Address
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=50, default='Brasil')

    # Step 3: Preferences
    membership_due_day = serializers.IntegerField(min_value=1, max_value=28)
    theme_preference = serializers.ChoiceField(
        choices=UserProfile.ThemeChoice.choices,
        default=UserProfile.ThemeChoice.WHITE
    )
    language_preference = serializers.ChoiceField(
        choices=UserProfile.LanguageChoice.choices,
        default=UserProfile.LanguageChoice.PT_BR
    )

    # Step 4: Terms acceptance
    terms_accepted = serializers.BooleanField()
    privacy_accepted = serializers.BooleanField()

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Terms must be accepted")
        return value

    def validate_privacy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Privacy policy must be accepted")
        return value

    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                f'Já existe um usuário cadastrado com o email {value}.'
            )
        return value

    def create(self, validated_data):
        """Create user with profile during onboarding"""
        # Create user (email uniqueness already validated)
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=User.objects.make_random_password()  # Will be set later via social auth or password reset
        )

        # Create profile manually (no signal configured)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': validated_data['phone'],
                'city': validated_data['city'],
                'state': validated_data['state'],
                'country': validated_data['country'],
                'membership_due_day': validated_data['membership_due_day'],
                'theme_preference': validated_data['theme_preference'],
                'language_preference': validated_data['language_preference'],
                'is_onboarding_completed': True
            }
        )

        # If profile already existed, update it
        if not created:
            profile.phone = validated_data['phone']
            profile.city = validated_data['city']
            profile.state = validated_data['state']
            profile.country = validated_data['country']
            profile.membership_due_day = validated_data['membership_due_day']
            profile.theme_preference = validated_data['theme_preference']
            profile.language_preference = validated_data['language_preference']
            profile.is_onboarding_completed = True
            profile.save()

        # Send webhook notification for new member
        self._send_webhook_notification(user)

        return user

    def _send_webhook_notification(self, user):
        """Send webhook notification to Kestra for new member email"""
        webhook_url = "https://n8n.texts.com.br/webhook-test/orbe_newmember_email"

        # Get language from user profile
        language = getattr(user.profile, 'language_preference', 'pt-br') if hasattr(user, 'profile') else 'pt-br'

        payload = {
            "first_name": user.first_name,
            "email": user.email,
            "user_id": user.id,
            "language": language,
            "registration_date": user.date_joined.isoformat() if user.date_joined else None,
        }

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ORBE-Platform/1.0'
                },
                timeout=10  # 10 second timeout
            )
            response.raise_for_status()
            logger.info(f"Webhook notification sent successfully for user {user.email}")
        except requests.RequestException as e:
            logger.error(f"Failed to send webhook notification for user {user.email}: {str(e)}")
            # Don't raise the exception to avoid breaking user registration

    def save(self, user=None):
        """Save onboarding data to user and profile (for existing users)"""
        validated_data = self.validated_data

        if user:
            # Update existing user
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            user.email = validated_data['email']
            user.save()

            # Update profile (create if doesn't exist)
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': validated_data['phone'],
                    'city': validated_data['city'],
                    'state': validated_data['state'],
                    'country': validated_data['country'],
                    'membership_due_day': validated_data['membership_due_day'],
                    'theme_preference': validated_data['theme_preference'],
                    'language_preference': validated_data['language_preference'],
                    'is_onboarding_completed': True
                }
            )

            # If profile already existed, update it
            if not created:
                profile.phone = validated_data['phone']
                profile.city = validated_data['city']
                profile.state = validated_data['state']
                profile.country = validated_data['country']
                profile.membership_due_day = validated_data['membership_due_day']
                profile.theme_preference = validated_data['theme_preference']
                profile.language_preference = validated_data['language_preference']
                profile.is_onboarding_completed = True
                profile.save()

            return user
        else:
            # Create new user
            return self.create(validated_data)


# ============================================================================
# INVITATION SYSTEM SERIALIZERS
# ============================================================================

class InvitationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating member invitations.
    Only accessible by Board/Admin users.
    """
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        default=User.Role.MEMBER,
        required=False
    )

    def validate_email(self, value):
        """Check if user or invitation already exists"""
        from .models import InvitationToken

        # Check if user already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Um usuário com este email já existe.")

        # Check if there's an active (unused, not expired) invitation
        active_invitation = InvitationToken.objects.filter(
            email=value,
            is_used=False
        ).first()

        if active_invitation and active_invitation.is_valid:
            raise serializers.ValidationError(
                "Já existe um convite ativo para este email. "
                f"Expira em {active_invitation.expires_at.strftime('%d/%m/%Y às %H:%M')}."
            )

        return value

    def create(self, validated_data):
        """Create invitation and send email"""
        from .models import InvitationToken
        from .utils.email_service import EmailService

        # Get current user (admin/board who is creating invitation)
        created_by = self.context['request'].user if 'request' in self.context else None

        # Create invitation token
        invitation = InvitationToken.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', User.Role.MEMBER),
            created_by=created_by
        )

        # Send invitation email via n8n webhook
        email_sent = EmailService.send_invitation_email(
            email=invitation.email,
            first_name=invitation.first_name,
            last_name=invitation.last_name,
            token=invitation.token,
            expires_in="7 dias"
        )

        if not email_sent:
            logger.warning(
                f"Invitation created for {invitation.email} but email failed to send. "
                "Token can still be used manually."
            )

        return invitation


class InvitationSerializer(serializers.Serializer):
    """Serializer for invitation token display"""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    is_used = serializers.BooleanField(read_only=True)
    used_at = serializers.DateTimeField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)


class TokenValidationSerializer(serializers.Serializer):
    """Serializer for validating invitation token"""
    token = serializers.CharField(required=True, min_length=32)

    def validate_token(self, value):
        """Validate that token exists and is valid"""
        from .models import InvitationToken

        try:
            invitation = InvitationToken.objects.get(token=value)

            if invitation.is_used:
                raise serializers.ValidationError(
                    "Este convite já foi utilizado."
                )

            if invitation.is_expired:
                raise serializers.ValidationError(
                    "Este convite expirou. Solicite um novo convite ao administrador."
                )

            # Store invitation in context for later use
            self.context['invitation'] = invitation

        except InvitationToken.DoesNotExist:
            raise serializers.ValidationError(
                "Token inválido ou não encontrado."
            )

        return value


class PasswordSetupSerializer(serializers.Serializer):
    """
    Serializer for setting up password with invitation token.
    Creates user account and activates it.
    """
    token = serializers.CharField(required=True, min_length=32)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    password_confirm = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate(self, attrs):
        """Validate passwords match and token is valid"""
        # Check passwords match
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })

        # Validate token
        from .models import InvitationToken

        try:
            invitation = InvitationToken.objects.get(token=attrs['token'])

            if invitation.is_used:
                raise serializers.ValidationError({
                    'token': 'Este convite já foi utilizado.'
                })

            if invitation.is_expired:
                raise serializers.ValidationError({
                    'token': 'Este convite expirou. Solicite um novo convite.'
                })

            # Store invitation in attrs for create method
            attrs['invitation'] = invitation

        except InvitationToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': 'Token inválido.'
            })

        return attrs

    def create(self, validated_data):
        """Create user account with password"""
        invitation = validated_data['invitation']
        password = validated_data['password']

        logger.info(f"🔐 Creating user with email: {invitation.email}, password length: {len(password)}")

        # Create user
        user = User.objects.create_user(
            username=invitation.email,  # Use email as username
            email=invitation.email,
            first_name=invitation.first_name,
            last_name=invitation.last_name,
            password=password,
            role=invitation.role,
            is_active=True,  # Account is immediately active
            registration_method=User.RegistrationMethod.INVITED  # Mark as invited user
        )

        # Create verified email address for allauth compatibility
        from allauth.account.models import EmailAddress
        EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={
                'verified': True,
                'primary': True
            }
        )

        # Verify password was set correctly
        if user.check_password(password):
            logger.info(f"✅ Password verification successful for {user.email}")
        else:
            logger.error(f"❌ Password verification FAILED for {user.email}")

        # Mark invitation as used
        invitation.mark_as_used()

        logger.info(f"✅ User account created for {user.email} via invitation system")

        return user
