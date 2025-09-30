"""
Custom adapters for django-allauth
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import secrets
import string

User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for ORBE platform"""

    def get_login_redirect_url(self, request):
        """Redirect to frontend after login"""
        return f"{settings.FRONTEND_URL}/dashboard"

    def get_signup_redirect_url(self, request):
        """Redirect to onboarding after signup"""
        return f"{settings.FRONTEND_URL}/onboarding"

    def save_user(self, request, user, form, commit=True):
        """Save user with additional processing"""
        user = super().save_user(request, user, form, commit)

        if commit:
            # Set user role as member by default
            user.role = User.Role.MEMBER

            # Generate temporary password for manual registration
            if not user.has_usable_password():
                temp_password = self.generate_temp_password()
                user.set_password(temp_password)

                # Send temporary password via email
                self.send_temp_password_email(user, temp_password)

            user.save()

        return user

    def generate_temp_password(self):
        """Generate secure temporary password"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))

    def send_temp_password_email(self, user, temp_password):
        """Send temporary password to user"""
        subject = _('Welcome to ORBE Platform - Temporary Password')

        context = {
            'user': user,
            'temp_password': temp_password,
            'login_url': f"{settings.FRONTEND_URL}/login",
            'site_name': 'ORBE Platform'
        }

        html_message = render_to_string(
            'account/email/temp_password_email.html',
            context
        )
        plain_message = render_to_string(
            'account/email/temp_password_email.txt',
            context
        )

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter"""

    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting social account"""
        return f"{settings.FRONTEND_URL}/profile"

    def populate_user(self, request, sociallogin, data):
        """Populate user data from social account"""
        user = super().populate_user(request, sociallogin, data)

        # Set default role for social users
        user.role = User.Role.MEMBER

        # Extract additional info from social account
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data

            # Get profile picture if available
            if 'picture' in extra_data and hasattr(user, 'profile'):
                user.profile.avatar_url = extra_data['picture']

        return user

    def save_user(self, request, sociallogin, form=None):
        """Save social user with additional processing"""
        user = super().save_user(request, sociallogin, form)

        # Mark as requiring onboarding
        if hasattr(user, 'profile'):
            user.profile.is_onboarding_completed = False
            user.profile.save()

        return user