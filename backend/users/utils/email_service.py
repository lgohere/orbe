"""
Email service for ORBE Platform
Sends emails via n8n webhook with RabbitMQ backing for reliability
"""

import logging
import requests
from django.conf import settings
from django.template.loader import render_to_string
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Professional email service with n8n webhook integration.

    Architecture:
    - Django sends payload to n8n webhook
    - n8n queues email in RabbitMQ (handles excess requests)
    - RabbitMQ ensures delivery even during high load
    - Email sent asynchronously without blocking Django
    """

    N8N_WEBHOOK_URL = "https://n8n.texts.com.br/webhook/orbe_member_invitation"

    @classmethod
    def send_invitation_email(
        cls,
        email: str,
        first_name: str,
        last_name: str,
        token: str,
        expires_in: str = "7 dias",
        language: str = "pt-BR"
    ) -> bool:
        """
        Send invitation email with password setup link.

        Args:
            email: Recipient email address
            first_name: Recipient first name
            last_name: Recipient last name
            token: Unique invitation token
            expires_in: Expiry period (default: "7 dias")
            language: Email language (default: "pt-BR")

        Returns:
            bool: True if webhook accepted the request, False otherwise
        """
        try:
            # Generate activation link
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            activation_link = f"{frontend_url}/set-password?token={token}"

            # Render HTML email template
            html_content = render_to_string('emails/invitation.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'activation_link': activation_link,
                'expires_in': expires_in,
            })

            # Prepare payload for n8n webhook
            payload = {
                "type": "invitation",
                "to": email,
                "recipient": {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                },
                "data": {
                    "activation_link": activation_link,
                    "token": token,
                    "expires_in": expires_in,
                    "language": language
                },
                "html_content": html_content,
                "subject": f"Bem-vindo à ORBE, {first_name}! 🎉",
                "priority": "high"  # RabbitMQ priority queue
            }

            logger.info(f"Sending invitation email to {email} via n8n webhook")

            # Send to n8n webhook (with RabbitMQ backing)
            response = requests.post(
                cls.N8N_WEBHOOK_URL,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ORBE-Platform/1.0',
                    'X-Source': 'django-invitation-system'
                },
                timeout=10  # 10 second timeout
            )

            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Invitation email queued successfully for {email} (Status: {response.status_code})")
                return True
            else:
                logger.error(
                    f"❌ n8n webhook returned error for {email}: "
                    f"Status {response.status_code}, Response: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout sending invitation email to {email} (n8n webhook)")
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error sending invitation email to {email}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"❌ Unexpected error sending invitation email to {email}: {str(e)}")
            return False

    @classmethod
    def send_welcome_email(
        cls,
        email: str,
        first_name: str,
        language: str = "pt-BR"
    ) -> bool:
        """
        Send welcome email after password setup and onboarding completion.

        Args:
            email: Recipient email address
            first_name: Recipient first name
            language: Email language (default: "pt-BR")

        Returns:
            bool: True if webhook accepted the request, False otherwise
        """
        try:
            payload = {
                "type": "welcome",
                "to": email,
                "recipient": {
                    "email": email,
                    "first_name": first_name
                },
                "data": {
                    "language": language,
                    "dashboard_link": f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/dashboard"
                },
                "subject": f"Bem-vindo à comunidade ORBE, {first_name}! 🌟",
                "priority": "normal"
            }

            logger.info(f"Sending welcome email to {email} via n8n webhook")

            response = requests.post(
                "https://n8n.texts.com.br/webhook-test/orbe_welcome_email",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ORBE-Platform/1.0'
                },
                timeout=10
            )

            return response.status_code in [200, 201, 202]

        except Exception as e:
            logger.error(f"Error sending welcome email to {email}: {str(e)}")
            return False