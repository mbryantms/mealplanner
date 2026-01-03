from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Authentication
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    # Password reset
    path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # Profile
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/password/", views.password_change, name="password_change"),
    # User management (admin only)
    path("manage/", views.user_list, name="user_list"),
    path("manage/create/", views.user_create, name="user_create"),
    path("manage/<int:pk>/edit/", views.user_edit, name="user_edit"),
    path("manage/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("manage/<int:pk>/reset-password/", views.user_reset_password, name="user_reset_password"),
]
