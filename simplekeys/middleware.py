import re
from django.conf import settings
from django.http import JsonResponse
from .verifier import verify, VerificationError, RateLimitError, QuotaError


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
                break
        else:
            return None

        key = request.META.get(getattr(settings, 'SIMPLEKEYS_HEADER',
                                       'HTTP_X_API_KEY'))
        if not key:
            key = request.GET.get(getattr(settings, 'SIMPLEKEYS_QUERY_PARAM',
                                          'apikey'))

        try:
            verify(key, zone)
        except VerificationError as e:
            return JsonResponse({'error': str(e)}, status=403)
        except RateLimitError as e:
            return JsonResponse({'error': str(e)}, status=429)
        except QuotaError as e:
            return JsonResponse({'error': str(e)}, status=429)

        # pass through
        return None
