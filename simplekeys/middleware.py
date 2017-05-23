import re
from .verifier import verify_request
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class SimpleKeysMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self._zones = None
        self.get_response = get_response

    @property
    def zones(self):
        if not self._zones:
            from django.conf import settings
            zones = getattr(settings, 'SIMPLEKEYS_ZONE_PATHS',
                            [('.*', 'default')])

            self._zones = [
                ((re.compile(path) if isinstance(path, str) else path), zone)
                for (path, zone) in zones
            ]
        return self._zones

    def process_request(self, request):
        for path, zone in self.zones:
            if path.match(request.path):
                return verify_request(request, zone)

        # no paths matched, pass-through
        return None
