"""
Custom authentication views with CSRF exemption for Token Authentication
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dj_rest_auth.views import LoginView as DjRestAuthLoginView
from dj_rest_auth.views import LogoutView as DjRestAuthLogoutView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(DjRestAuthLoginView):
    """
    Login view with CSRF exemption and role-based access control.

    Rules:
    - Staff/Admin (SUPER_ADMIN, BOARD, FISCAL_COUNCIL): Can login directly
    - Invited Members (MEMBER with registration_method='invited'): Must use invitation token
    - Manual Members (MEMBER with registration_method='manual'): Can login directly
    """

    def post(self, request, *args, **kwargs):
        # Get email from request to check user before authentication
        email = request.data.get('email')

        if email:
            try:
                user = User.objects.get(email=email)

                # Check if this is an invited member trying to login directly
                if user.requires_invitation:
                    return Response({
                        'non_field_errors': [
                            'Este usuário foi convidado e deve criar senha através do link enviado por email. '
                            'Verifique sua caixa de entrada.'
                        ]
                    }, status=status.HTTP_403_FORBIDDEN)

                # Check if invited user hasn't completed onboarding
                if (user.registration_method == User.RegistrationMethod.INVITED and
                    hasattr(user, 'profile') and
                    not user.profile.is_onboarding_completed):
                    return Response({
                        'non_field_errors': [
                            'Por favor, complete o processo de onboarding antes de fazer login.'
                        ]
                    }, status=status.HTTP_403_FORBIDDEN)

            except User.DoesNotExist:
                pass  # Let Django handle invalid credentials

        # Proceed with normal login
        return super().post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(DjRestAuthLogoutView):
    """
    Logout view with CSRF exemption.
    """
    pass
