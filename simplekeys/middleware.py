from django.conf import settings
from django.http import JsonResponse
from .verifier import verify, VerificationError, RateLimitError, QuotaError


class SimpleKeysMiddleware(object):
    def __init__(self, zone=None):
        if zone is None:
            self.zone = getattr(settings, 'SIMPLEKEYS_DEFAULT_ZONE', 'default')
        else:
            self.zone = zone

    def process_request(self, request):
        key = request.META.get(getattr(settings, 'SIMPLEKEYS_HEADER',
                                       'HTTP_X_API_KEY'))
        if not key:
            key = request.GET.get(getattr(settings, 'SIMPLEKEYS_QUERY_PARAM',
                                          'apikey'))

        try:
            verify(key, self.zone)
        except VerificationError as e:
            return JsonResponse({'error': str(e)}, status=403)
        except RateLimitError as e:
            return JsonResponse({'error': str(e)}, status=429)
        except QuotaError as e:
            return JsonResponse({'error': str(e)}, status=429)

        # pass through
        return None
