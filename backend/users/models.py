"""
User models for ORBE Platform
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import secrets


class User(AbstractUser):
    """
    Custom User model with additional fields for ORBE platform
    """

    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', _('Super Admin')
        BOARD = 'board', _('Diretoria')
        FISCAL_COUNCIL = 'fiscal_council', _('Conselho Fiscal')
        MEMBER = 'member', _('Membro')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    # Override username field to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_board_member(self):
        return self.role == self.Role.BOARD

    @property
    def is_fiscal_council_member(self):
        return self.role == self.Role.FISCAL_COUNCIL

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def can_approve_cases(self):
        return self.role in [self.Role.FISCAL_COUNCIL, self.Role.SUPER_ADMIN]

    @property
    def can_create_cases(self):
        return self.role in [self.Role.BOARD, self.Role.SUPER_ADMIN]


class UserProfile(models.Model):
    """
    Extended user profile with additional information
    """

    class ThemeChoice(models.TextChoices):
        WHITE = 'white', _('White')
        BLACK = 'black', _('Black')

    class LanguageChoice(models.TextChoices):
        PT_BR = 'pt-br', _('Português (Brasil)')
        EN = 'en', _('English')
        ES = 'es', _('Español')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Contact information
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True
    )

    # Address information
    address_line1 = models.CharField(
        _('address line 1'),
        max_length=255,
        blank=True
    )
    address_line2 = models.CharField(
        _('address line 2'),
        max_length=255,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True
    )
    state = models.CharField(
        _('state'),
        max_length=50,
        blank=True
    )
    zip_code = models.CharField(
        _('zip code'),
        max_length=20,
        blank=True
    )
    country = models.CharField(
        _('country'),
        max_length=50,
        default='Brasil'
    )

    # Membership information
    membership_due_day = models.PositiveIntegerField(
        _('membership due day'),
        default=5,
        help_text=_('Day of the month when membership fee is due (1-28)')
    )

    # UI/UX preferences
    theme_preference = models.CharField(
        _('theme preference'),
        max_length=10,
        choices=ThemeChoice.choices,
        default=ThemeChoice.WHITE
    )
    language_preference = models.CharField(
        _('language preference'),
        max_length=10,
        choices=LanguageChoice.choices,
        default=LanguageChoice.PT_BR
    )

    # Onboarding
    is_onboarding_completed = models.BooleanField(
        _('onboarding completed'),
        default=False
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.email} - Profile"

    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.zip_code,
            self.country
        ]
        return ", ".join([part for part in parts if part])


# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class InvitationToken(models.Model):
    """
    Token for new member invitation and password setup.
    Admin/Board creates invitation → Email sent with token link →
    User clicks link → Sets password → Account activated
    """
    email = models.EmailField(
        verbose_name=_('Email'),
        unique=True,
        help_text=_('Email address for the invited member')
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('Token'),
        help_text=_('Unique token for password setup')
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name=_('First Name')
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_('Last Name')
    )
    role = models.CharField(
        max_length=20,
        choices=User.Role.choices,
        default=User.Role.MEMBER,
        verbose_name=_('Role')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_invitations',
        verbose_name=_('Created By'),
        help_text=_('Admin/Board member who created this invitation')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('Expires At'),
        help_text=_('Token expiration date (7 days from creation)')
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_('Is Used'),
        help_text=_('Whether the invitation has been used')
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Used At')
    )

    class Meta:
        verbose_name = _('Invitation Token')
        verbose_name_plural = _('Invitation Tokens')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_used']),
            models.Index(fields=['token', 'is_used']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        status = 'Used' if self.is_used else ('Expired' if self.is_expired else 'Active')
        return f"Invitation for {self.email} ({status})"

    def save(self, *args, **kwargs):
        """Generate token and expiry if not set"""
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            # Token expires in 7 days
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired

    def mark_as_used(self):
        """Mark invitation as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])