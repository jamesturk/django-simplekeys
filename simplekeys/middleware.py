import re
from .verifier import verify_request


class SimpleKeysMiddleware(object):
    def __init__(self):
        self._zones = None

    @property
    def zones(self):
        if not self._zones:
            from django.conf import settings
            zones = getattr(settings, 'SIMPLEKEYS_ZONES',
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
