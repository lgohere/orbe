"""
Views for users app
"""

from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import UserProfile
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    OnboardingSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
    TokenValidationSerializer,
    PasswordSetupSerializer
)

User = get_user_model()


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get and update current user information"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRoleListView(generics.ListAPIView):
    """List all available user roles"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        roles = [
            {'value': choice[0], 'label': choice[1]}
            for choice in User.Role.choices
        ]
        return Response({'roles': roles})


class OnboardingView(generics.CreateAPIView):
    """Complete user onboarding process"""

    serializer_class = OnboardingSerializer
    permission_classes = []  # Allow unauthenticated users to register

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check if user is authenticated (existing user) or creating new user
            if request.user.is_authenticated:
                user = serializer.save(request.user)
            else:
                # Create new user
                user = serializer.save()

            user_serializer = UserSerializer(user)

            return Response({
                'message': _('Onboarding completed successfully'),
                'user': user_serializer.data,
                'is_new_user': not request.user.is_authenticated
            }, status=status.HTTP_201_CREATED if not request.user.is_authenticated else status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OnboardingStatusView(generics.RetrieveAPIView):
    """Check onboarding status"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile

        return Response({
            'is_completed': profile.is_onboarding_completed,
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'has_social_auth': user.socialaccount_set.exists(),
            },
            'profile': {
                'phone': profile.phone,
                'address_line1': profile.address_line1,
                'city': profile.city,
                'membership_due_day': profile.membership_due_day,
                'theme_preference': profile.theme_preference,
                'language_preference': profile.language_preference,
            }
        })


class PreferencesView(generics.UpdateAPIView):
    """Update user preferences (theme, language, location, contact)"""

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        profile = request.user.profile

        # Update theme preference
        if 'theme_preference' in request.data:
            theme = request.data['theme_preference']
            if theme in [choice[0] for choice in UserProfile.ThemeChoice.choices]:
                profile.theme_preference = theme

        # Update language preference
        if 'language_preference' in request.data:
            language = request.data['language_preference']
            if language in [choice[0] for choice in UserProfile.LanguageChoice.choices]:
                profile.language_preference = language

        # Update membership due day
        if 'membership_due_day' in request.data:
            due_day = request.data['membership_due_day']
            if isinstance(due_day, int) and 1 <= due_day <= 28:
                profile.membership_due_day = due_day

        # Update contact information
        if 'phone' in request.data:
            profile.phone = request.data['phone']

        # Update location information
        if 'country' in request.data:
            profile.country = request.data['country']

        if 'city' in request.data:
            profile.city = request.data['city']

        if 'state' in request.data:
            profile.state = request.data['state']

        profile.save()

        return Response({
            'message': _('Preferences updated successfully'),
            'theme_preference': profile.theme_preference,
            'language_preference': profile.language_preference,
            'membership_due_day': profile.membership_due_day,
            'phone': profile.phone,
            'country': profile.country,
            'city': profile.city,
            'state': profile.state,
        })


class HealthCheckView(generics.GenericAPIView):
    """Health check endpoint"""

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({
            'status': 'healthy',
            'service': 'orbe-platform-api'
        })


# ============================================================================
# INVITATION SYSTEM VIEWS
# ============================================================================

class IsBoardOrAdmin(permissions.BasePermission):
    """Custom permission: Only Board or Admin users"""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.BOARD, User.Role.SUPER_ADMIN]
        )


class InvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing member invitations.

    Endpoints:
    - POST /api/users/invitations/ - Create invitation (Board/Admin only)
    - GET /api/users/invitations/ - List invitations (Board/Admin only)
    - POST /api/users/invitations/validate-token/ - Validate token (public)
    - POST /api/users/invitations/setup-password/ - Setup password (public)
    """
    from .models import InvitationToken

    queryset = InvitationToken.objects.all()
    serializer_class = InvitationSerializer

    def get_permissions(self):
        """
        - create, list, retrieve: Board/Admin only
        - validate_token, setup_password: Public (no auth required)
        """
        if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsBoardOrAdmin()]
        return []  # Public access for validate_token and setup_password

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return InvitationCreateSerializer
        elif self.action == 'validate_token':
            return TokenValidationSerializer
        elif self.action == 'setup_password':
            return PasswordSetupSerializer
        return InvitationSerializer

    def get_queryset(self):
        """Filter invitations based on user role"""
        user = self.request.user
        if user.is_authenticated and user.role in [User.Role.BOARD, User.Role.SUPER_ADMIN]:
            return self.queryset.order_by('-created_at')
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        """Create new invitation and send email"""
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            invitation = serializer.save()

            return Response({
                'message': 'Convite criado e email enviado com sucesso!',
                'invitation': {
                    'id': invitation.id,
                    'email': invitation.email,
                    'first_name': invitation.first_name,
                    'last_name': invitation.last_name,
                    'role': invitation.role,
                    'expires_at': invitation.expires_at,
                    'token': invitation.token  # Include token for admin reference
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='validate-token')
    def validate_token(self, request):
        """
        Validate invitation token.
        Public endpoint - no authentication required.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            invitation = serializer.context.get('invitation')

            return Response({
                'valid': True,
                'message': 'Token válido!',
                'invitation': {
                    'email': invitation.email,
                    'first_name': invitation.first_name,
                    'last_name': invitation.last_name,
                    'expires_at': invitation.expires_at
                }
            })

        return Response({
            'valid': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='setup-password')
    def setup_password(self, request):
        """
        Setup password and create user account.
        Public endpoint - no authentication required.
        Returns auth token for immediate login.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Create user account
            user = serializer.save()

            # Generate auth token for immediate login
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)

            # Return user data and token
            user_serializer = UserSerializer(user)

            return Response({
                'message': 'Conta criada com sucesso! Bem-vindo à ORBE!',
                'user': user_serializer.data,
                'token': token.key,
                'next_step': 'dashboard'  # Invited users go directly to dashboard
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)