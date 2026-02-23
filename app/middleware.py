from django.utils import timezone
from ipaddress import ip_address as ip_parse

from .models import VisitorLog


class VisitorLoggingMiddleware:
    """
    Middleware that logs basic visit metadata: IP, path, method, referrer,
    user agent, timestamp, and a simple location hint (if provided by proxy headers).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip logging for static/admin if desired
        path = request.path or ""
        if path.startswith("/static") or path.startswith("/admin"):
            return response

        try:
            ip = self._get_client_ip(request)
            location = self._get_location_hint(request)

            VisitorLog.objects.create(
                user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                ip_address=ip,
                path=path[:512],
                method=request.method[:10],
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:1024],
                referrer=(request.META.get("HTTP_REFERER") or "")[:1024],
                location=location[:255] if location else "Unknown",
                visited_at=timezone.now(),
            )
        except Exception:
            # Swallow logging errors to never block user traffic
            pass

        return response

    def _get_client_ip(self, request):
        # Trust X-Forwarded-For first (left-most, per common proxy setups)
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_candidate = None
        if xff:
            ip_candidate = xff.split(",")[0].strip()
        else:
            ip_candidate = request.META.get("REMOTE_ADDR")

        # Validate and normalize
        try:
            return str(ip_parse(ip_candidate)) if ip_candidate else None
        except Exception:
            return None

    def _get_location_hint(self, request):
        """
        Tries to derive a simple location hint from common proxy/CDN headers.
        This is best-effort and can be replaced with a GeoIP service if needed.
        """
        # Cloudflare country code or generic GeoIP city header if available
        country = request.META.get("HTTP_CF_IPCOUNTRY")
        city = request.META.get("HTTP_X_CITY")
        region = request.META.get("HTTP_X_REGION")

        parts = [part for part in [city, region, country] if part]
        return ", ".join(parts) if parts else "Unknown"

