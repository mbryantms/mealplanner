from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .forms import (
    AdminUserUpdateForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    LoginForm,
    UserCreateForm,
    UserUpdateForm,
)
from .decorators import admin_required

User = get_user_model()


class CustomLoginView(LoginView):
    """Custom login view with styled form."""

    form_class = LoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("recipes:recipe_list")


class CustomLogoutView(LogoutView):
    """Custom logout view."""

    next_page = reverse_lazy("users:login")


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view."""

    form_class = CustomPasswordResetForm
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view."""

    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirm view."""

    form_class = CustomSetPasswordForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view."""

    template_name = "users/password_reset_complete.html"


@login_required
def profile(request):
    """User profile view."""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    """Edit user profile."""
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("users:profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "users/profile_edit.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def password_change(request):
    """Change password view."""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("users:profile")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "users/password_change.html", {"form": form})


# Admin-only views for user management


@login_required
@admin_required
def user_list(request):
    """List all users (admin only)."""
    users = User.objects.all().order_by("username")
    return render(request, "users/user_list.html", {"users": users})


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def user_create(request):
    """Create new user (admin only)."""
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User '{user.username}' created successfully.")
            return redirect("users:user_list")
    else:
        form = UserCreateForm()

    return render(request, "users/user_form.html", {"form": form, "action": "Create"})


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def user_edit(request, pk):
    """Edit user (admin only)."""
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect("users:user_list")
    else:
        form = AdminUserUpdateForm(instance=user)

    return render(
        request, "users/user_form.html", {"form": form, "action": "Edit", "user": user}
    )


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def user_delete(request, pk):
    """Delete user (admin only)."""
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("users:user_list")

    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted successfully.")
        return redirect("users:user_list")

    return render(request, "users/user_delete.html", {"user": user})


@login_required
@admin_required
@require_http_methods(["POST"])
def user_reset_password(request, pk):
    """Reset user password (admin only) - sends reset email."""
    user = get_object_or_404(User, pk=pk)

    if user.email:
        form = CustomPasswordResetForm({"email": user.email})
        if form.is_valid():
            form.save(
                request=request,
                email_template_name="users/password_reset_email.html",
                subject_template_name="users/password_reset_subject.txt",
            )
            messages.success(
                request, f"Password reset email sent to {user.email}."
            )
    else:
        messages.error(
            request, f"User '{user.username}' does not have an email address."
        )

    return redirect("users:user_list")
