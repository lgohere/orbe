"""
Admin configuration for users app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import UserProfile, InvitationToken

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom user model"""

    inlines = [UserProfileInline]

    # Fields to display in user list
    list_display = [
        'email', 'username', 'first_name', 'last_name',
        'role', 'is_active', 'is_staff', 'date_joined'
    ]

    # Fields to filter by
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'last_login'
    ]

    # Fields to search
    search_fields = ['email', 'username', 'first_name', 'last_name']

    # Ordering
    ordering = ['-date_joined']

    # Fields in user detail/edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('ORBE Information'), {
            'fields': ('role',)
        }),
    )

    # Fields in user creation form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('ORBE Information'), {
            'fields': ('email', 'role')
        }),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for user profile"""

    list_display = [
        'user', 'phone', 'city', 'state', 'membership_due_day',
        'theme_preference', 'language_preference', 'is_onboarding_completed'
    ]

    list_filter = [
        'theme_preference', 'language_preference', 'is_onboarding_completed',
        'country', 'state', 'created_at'
    ]

    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'phone', 'city', 'state'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        (_('User'), {
            'fields': ['user']
        }),
        (_('Contact Information'), {
            'fields': ['phone']
        }),
        (_('Address'), {
            'fields': [
                'address_line1', 'address_line2', 'city',
                'state', 'zip_code', 'country'
            ]
        }),
        (_('Membership'), {
            'fields': ['membership_due_day']
        }),
        (_('Preferences'), {
            'fields': ['theme_preference', 'language_preference']
        }),
        (_('Onboarding'), {
            'fields': ['is_onboarding_completed']
        }),
        (_('Timestamps'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


# ============================================================================
# INVITATION TOKEN ADMIN
# ============================================================================

@admin.register(InvitationToken)
class InvitationTokenAdmin(admin.ModelAdmin):
    """
    Admin for invitation tokens.
    Allows Board/Admin to create invitations and send emails.
    """

    list_display = [
        'email',
        'full_name',
        'role',
        'status_badge',
        'created_by',
        'created_at',
        'expires_at',
        'used_at',
    ]

    list_filter = [
        'role',
        'is_used',
        'created_at',
        'expires_at',
    ]

    search_fields = [
        'email',
        'first_name',
        'last_name',
        'token',
    ]

    readonly_fields = [
        'token',
        'created_at',
        'expires_at',
        'is_used',
        'used_at',
        'is_expired',
        'is_valid',
        'token_link',
    ]

    fieldsets = [
        (_('Invited Member Information'), {
            'fields': ['email', 'first_name', 'last_name', 'role']
        }),
        (_('Token Information'), {
            'fields': ['token', 'token_link', 'expires_at', 'is_expired', 'is_valid']
        }),
        (_('Usage Status'), {
            'fields': ['is_used', 'used_at']
        }),
        (_('Metadata'), {
            'fields': ['created_by', 'created_at'],
            'classes': ['collapse']
        }),
    ]

    ordering = ['-created_at']

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields + ['email', 'first_name', 'last_name', 'role']
        return self.readonly_fields

    @admin.display(description='Full Name')
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description='Status')
    def status_badge(self, obj):
        """Display colored status badge"""
        from django.utils.html import format_html

        if obj.is_used:
            color = 'green'
            text = '✓ Used'
        elif obj.is_expired:
            color = 'red'
            text = '✗ Expired'
        else:
            color = 'orange'
            text = '● Active'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )

    @admin.display(description='Invitation Link')
    def token_link(self, obj):
        """Display copyable invitation link"""
        from django.utils.html import format_html
        from django.conf import settings

        if obj:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            link = f"{frontend_url}/set-password?token={obj.token}"

            return format_html(
                '<div style="font-family: monospace; background: #f5f5f5; padding: 10px; border-radius: 4px; margin: 5px 0;">'
                '<a href="{}" target="_blank" style="color: #304E69; text-decoration: none;">{}</a>'
                '<br><small style="color: #666;">Click to open | Copy link to send manually</small>'
                '</div>',
                link,
                link
            )
        return '-'

    def save_model(self, request, obj, form, change):
        """
        Save model and send invitation email.
        Set created_by to current user.
        """
        if not change:  # Creating new invitation
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

        # Send invitation email if new invitation
        if not change:
            from .utils.email_service import EmailService
            import logging

            logger = logging.getLogger(__name__)

            email_sent = EmailService.send_invitation_email(
                email=obj.email,
                first_name=obj.first_name,
                last_name=obj.last_name,
                token=obj.token,
                expires_in="7 dias"
            )

            if email_sent:
                self.message_user(
                    request,
                    f'✅ Convite criado e email enviado para {obj.email}',
                    level='SUCCESS'
                )
            else:
                self.message_user(
                    request,
                    f'⚠️ Convite criado mas email falhou. Use o link manual acima.',
                    level='WARNING'
                )

    actions = ['resend_invitation_email']

    @admin.action(description='🔄 Reenviar email de convite')
    def resend_invitation_email(self, request, queryset):
        """Resend invitation emails for selected invitations"""
        from .utils.email_service import EmailService

        sent_count = 0
        failed_count = 0

        for invitation in queryset.filter(is_used=False):
            if invitation.is_expired:
                self.message_user(
                    request,
                    f'❌ Convite para {invitation.email} está expirado. Crie um novo.',
                    level='ERROR'
                )
                continue

            email_sent = EmailService.send_invitation_email(
                email=invitation.email,
                first_name=invitation.first_name,
                last_name=invitation.last_name,
                token=invitation.token,
                expires_in="7 dias"
            )

            if email_sent:
                sent_count += 1
            else:
                failed_count += 1

        if sent_count > 0:
            self.message_user(
                request,
                f'✅ {sent_count} email(s) enviado(s) com sucesso!',
                level='SUCCESS'
            )

        if failed_count > 0:
            self.message_user(
                request,
                f'⚠️ {failed_count} email(s) falharam.',
                level='WARNING'
            )