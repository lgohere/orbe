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
    PasswordSetupSerializer,
    MemberListSerializer,
    MemberDetailSerializer,
    UserAutocompleteSerializer
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


class IsAdminOnly(permissions.BasePermission):
    """Custom permission: Only Super Admin users"""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.SUPER_ADMIN
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


# ============================================================================
# MEMBERS MANAGEMENT VIEWS (ADMIN ONLY)
# ============================================================================

class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing members (Admin only).

    Endpoints:
    - GET /api/users/members/ - List all members with financial summary
    - GET /api/users/members/:id/ - Get detailed member info
    - GET /api/users/members/stats/ - Get overall members statistics
    """

    permission_classes = [IsAdminOnly]

    def get_queryset(self):
        """
        Get all users with optional filtering.

        Query params:
        - role: Filter by role (MEMBER, BOARD, FISCAL_COUNCIL, SUPER_ADMIN)
        - is_active: Filter by active status (true/false)
        - search: Search by name or email
        - has_overdue: Filter members with overdue fees (true/false)
        """
        queryset = User.objects.select_related('profile').all()

        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # Filter members with overdue fees
        has_overdue = self.request.query_params.get('has_overdue')
        if has_overdue and has_overdue.lower() == 'true':
            from finance.models import MembershipFee
            overdue_user_ids = MembershipFee.objects.filter(
                status='overdue'
            ).values_list('user_id', flat=True).distinct()
            queryset = queryset.filter(id__in=overdue_user_ids)

        return queryset.order_by('-date_joined')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return MemberDetailSerializer
        return MemberListSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get overall members statistics.

        Returns:
        - Total members
        - Active/inactive members
        - Members by role
        - Financial overview
        - Recent registrations
        """
        from finance.models import MembershipFee, VoluntaryDonation
        from django.db.models import Sum, Count, Q
        from datetime import date, timedelta

        # Total members
        total_members = User.objects.count()
        active_members = User.objects.filter(is_active=True).count()
        inactive_members = total_members - active_members

        # Members by role
        members_by_role = {}
        for role_value, role_label in User.Role.choices:
            count = User.objects.filter(role=role_value).count()
            members_by_role[role_value] = {
                'label': role_label,
                'count': count
            }

        # Financial overview
        total_fees_collected = MembershipFee.objects.filter(
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_donations_collected = VoluntaryDonation.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        pending_fees_count = MembershipFee.objects.filter(status='pending').count()
        overdue_fees_count = MembershipFee.objects.filter(status='overdue').count()

        # Members with financial issues
        members_with_overdue = User.objects.filter(
            membership_fees__status='overdue'
        ).distinct().count()

        # Recent registrations (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_registrations = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()

        # Registration method breakdown
        registration_methods = {}
        for method_value, method_label in User.RegistrationMethod.choices:
            count = User.objects.filter(registration_method=method_value).count()
            registration_methods[method_value] = {
                'label': method_label,
                'count': count
            }

        return Response({
            'overview': {
                'total_members': total_members,
                'active_members': active_members,
                'inactive_members': inactive_members,
                'recent_registrations_30d': recent_registrations
            },
            'by_role': members_by_role,
            'financial': {
                'total_fees_collected': float(total_fees_collected),
                'total_donations_collected': float(total_donations_collected),
                'total_revenue': float(total_fees_collected + total_donations_collected),
                'pending_fees_count': pending_fees_count,
                'overdue_fees_count': overdue_fees_count,
                'members_with_overdue': members_with_overdue
            },
            'registration_methods': registration_methods
        })

    @action(detail=True, methods=['patch'])
    def update_role(self, request, pk=None):
        """
        Update member role.

        Body: { "role": "BOARD" | "FISCAL_COUNCIL" | "MEMBER" | "SUPER_ADMIN" }
        """
        member = self.get_object()
        new_role = request.data.get('role')

        if not new_role:
            return Response(
                {'error': 'Role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate role
        valid_roles = [choice[0] for choice in User.Role.choices]
        if new_role not in valid_roles:
            return Response(
                {'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent changing own role
        if member.id == request.user.id:
            return Response(
                {'error': 'Você não pode alterar sua própria role'},
                status=status.HTTP_403_FORBIDDEN
            )

        old_role = member.role
        member.role = new_role
        member.save()

        return Response({
            'message': f'Role atualizada de {old_role} para {new_role}',
            'member': MemberListSerializer(member).data
        })

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Activate/deactivate member account.
        """
        member = self.get_object()

        # Prevent deactivating own account
        if member.id == request.user.id:
            return Response(
                {'error': 'Você não pode desativar sua própria conta'},
                status=status.HTTP_403_FORBIDDEN
            )

        member.is_active = not member.is_active
        member.save()

        action_text = 'ativada' if member.is_active else 'desativada'

        return Response({
            'message': f'Conta {action_text} com sucesso',
            'member': MemberListSerializer(member).data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def autocomplete(self, request):
        """
        Lightweight endpoint for autocomplete/search fields.
        Returns only id, email, and full_name for quick lookups.

        Query params:
        - search: Search by name or email
        - is_active: Filter by active status (default: true)
        - limit: Max results (default: 20)
        """
        queryset = User.objects.all()

        # Filter by active status (default to true)
        is_active = request.query_params.get('is_active', 'true')
        queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Search by name or email
        search = request.query_params.get('search', '')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # Limit results
        limit = int(request.query_params.get('limit', 20))
        queryset = queryset[:limit]

        serializer = UserAutocompleteSerializer(queryset, many=True)
        return Response(serializer.data)