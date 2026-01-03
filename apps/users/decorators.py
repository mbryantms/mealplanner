from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Role


def admin_required(view_func):
    """Decorator that checks if the user has admin role."""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")

        if request.user.role != Role.ADMIN and not request.user.is_superuser:
            messages.error(
                request, "You do not have permission to access this page."
            )
            return redirect("recipes:recipe_list")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
