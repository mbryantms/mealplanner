"""
URL configuration for Family Meal Planner.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # App URLs will be added here as features are implemented
    # path("", include("apps.recipes.urls")),
    # path("plan/", include("apps.planning.urls")),
    # path("shopping/", include("apps.shopping.urls")),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
