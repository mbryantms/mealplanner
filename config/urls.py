"""
URL configuration for Family Meal Planner.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.decorators.cache import cache_control
from django.views.generic import RedirectView


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(request):
    """Serve the service worker from the root path."""
    sw_path = settings.STATIC_ROOT / "sw.js" if not settings.DEBUG else settings.BASE_DIR / "static" / "sw.js"
    try:
        with open(sw_path, "r") as f:
            return HttpResponse(f.read(), content_type="application/javascript")
    except FileNotFoundError:
        return HttpResponse("// Service worker not found", content_type="application/javascript", status=404)


def health_check(request):
    """Health check endpoint for container orchestration."""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HttpResponse("OK", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Error: {e}", content_type="text/plain", status=503)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.users.urls")),
    path("recipes/", include("apps.recipes.urls")),
    path("plan/", include("apps.planning.urls")),
    path("shopping/", include("apps.shopping.urls")),
    path("stats/", include("apps.stats.urls")),
    # PWA service worker - must be served from root for scope
    path("sw.js", service_worker, name="service_worker"),
    # Health check for container orchestration
    path("health/", health_check, name="health_check"),
    # Redirect root to meal planning calendar
    path("", RedirectView.as_view(pattern_name="planning:calendar", permanent=False), name="home"),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
