"""
Custom middleware for ORBE Platform
"""

from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Disable CSRF validation for API endpoints.

    We use Token Authentication for API endpoints, which doesn't require CSRF.
    CSRF protection is still enabled for Django Admin and other form-based views.
    """

    def process_request(self, request):
        # Skip CSRF check for all /api/ endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
