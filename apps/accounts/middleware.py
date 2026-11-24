"""Middleware for the accounts app."""
from django.utils import timezone


class RoleMiddleware:
    """Refresh ``user.last_active`` on every request and expose role helpers.

    This middleware does NOT gate access - per-view permission decorators do
    that. It only updates activity timestamps so the directory can show who
    is recently active.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'user', None) is not None and request.user.is_authenticated:
            # Cheap update - only save last_active, avoid touching related fields
            User = request.user.__class__
            User.objects.filter(pk=request.user.pk).update(last_active=timezone.now())
        return self.get_response(request)
