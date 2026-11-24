"""Template context processors for accounts."""
from .models import Role


def user_roles(request):
    """Expose the available role choices and the user's current roles."""
    ctx = {
        'all_roles': Role.ROLE_CHOICES,
    }
    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        ctx['user_role_names'] = [r.name for r in user.roles.all()]
        ctx['user_role_labels'] = [r.get_name_display() for r in user.roles.all()]
    else:
        ctx['user_role_names'] = []
        ctx['user_role_labels'] = []
    return ctx
