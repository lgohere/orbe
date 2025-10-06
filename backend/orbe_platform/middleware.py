"""
Custom middleware for ORBE Platform
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Disable CSRF validation for API endpoints.

    We use Token Authentication for API endpoints, which doesn't require CSRF.
    CSRF protection is still enabled for Django Admin and other form-based views.
    """

    def process_request(self, request):
        # Skip CSRF check for all /api/ endpoints
        if not request.path.startswith('/api/'):
            return

        token_header = request.META.get('HTTP_AUTHORIZATION')
        exempt_paths = getattr(settings, 'CSRF_EXEMPT_API_PATHS', [])

        if token_header or request.path in exempt_paths:
            setattr(request, '_dont_enforce_csrf_checks', True)
