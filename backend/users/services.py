"""
Email services for user management
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .models import User


class EmailService:
    """Service for sending emails to users"""

    @staticmethod
    def send_welcome_email_with_password_reset(user: User):
        """
        Send welcome email with password reset link for new users
        More secure than sending temporary password
        """
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct password reset URL
        # This will be handled by frontend
        reset_url = f"{settings.FRONTEND_URL}/auth/set-password?uid={uid}&token={token}"

        # Email context
        context = {
            'user': user,
            'reset_url': reset_url,
            'login_url': f"{settings.FRONTEND_URL}/auth/login",
            'site_name': 'ORBE Platform',
        }

        # Render email templates
        subject = 'Bem-vindo(a) à Plataforma ORBE - Defina sua senha'

        html_message = render_to_string(
            'account/email/welcome_password_reset.html',
            context
        )

        text_message = render_to_string(
            'account/email/welcome_password_reset.txt',
            context
        )

        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    @staticmethod
    def send_temp_password_email(user: User, temp_password: str):
        """
        Send temporary password email (legacy approach)
        Less secure but simpler
        """
        context = {
            'user': user,
            'temp_password': temp_password,
            'login_url': f"{settings.FRONTEND_URL}/auth/login",
        }

        subject = 'Bem-vindo(a) à Plataforma ORBE - Sua senha temporária'

        html_message = render_to_string(
            'account/email/temp_password_email.html',
            context
        )

        send_mail(
            subject=subject,
            message=f'Sua senha temporária: {temp_password}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True