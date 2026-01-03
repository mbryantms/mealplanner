from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Custom login form with Tailwind styling."""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm",
                "placeholder": "Password",
            }
        )
    )


class UserCreateForm(UserCreationForm):
    """Form for creating new users (admin only)."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            )


class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            )


class AdminUserUpdateForm(forms.ModelForm):
    """Form for admins to update any user, including role."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = (
                    "h-4 w-4 rounded border-gray-300 text-blue-600 "
                    "focus:ring-blue-500"
                )
            else:
                field.widget.attrs["class"] = (
                    "block w-full rounded-md border-gray-300 shadow-sm "
                    "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                )


class CustomPasswordChangeForm(PasswordChangeForm):
    """Password change form with Tailwind styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            )


class CustomPasswordResetForm(PasswordResetForm):
    """Password reset form with Tailwind styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["class"] = (
            "block w-full rounded-md border-gray-300 shadow-sm "
            "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        )
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email address"


class CustomSetPasswordForm(SetPasswordForm):
    """Set password form with Tailwind styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "block w-full rounded-md border-gray-300 shadow-sm "
                "focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            )
