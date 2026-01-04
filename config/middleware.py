"""Custom middleware for the application."""

from django.conf import settings


class FrameOptionsMiddleware:
    """
    Middleware to set Content-Security-Policy frame-ancestors header.

    This allows the app to be embedded in iframes from specific domains
    (like Home Assistant) while still protecting against clickjacking
    from unauthorized domains.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Get allowed frame ancestors from settings
        frame_ancestors = getattr(settings, "FRAME_ANCESTORS", ["'self'"])

        if frame_ancestors:
            # Build the CSP frame-ancestors directive
            ancestors = " ".join(frame_ancestors)
            response["Content-Security-Policy"] = f"frame-ancestors {ancestors}"

            # Remove X-Frame-Options if we're using CSP frame-ancestors
            # CSP takes precedence, but some browsers check both
            if "X-Frame-Options" in response:
                del response["X-Frame-Options"]

        return response
