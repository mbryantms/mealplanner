from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"


class User(AbstractUser):
    """Custom user model with role field for admin/user permissions."""

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        help_text="User role determines permissions within the application.",
    )

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username

    @property
    def is_admin_role(self):
        """Check if user has admin role (not Django's is_staff)."""
        return self.role == Role.ADMIN
