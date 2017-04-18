from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import decorator_from_middleware
from .verifier import verify, VerificationError, RateLimitError, QuotaError


class SimpleKeyMiddleware(object):
    def process_request(self, request):
        key = request.META.get(getattr(settings, 'SIMPLEKEY_HEADER', 'HTTP_X_API_KEY'))
        if not key:
            key = request.GET.get(getattr(settings, 'SIMPLEKEY_QUERY_PARAM', 'apikey'))
        zone = getattr(settings, 'SIMPLEKEY_DEFAULT_ZONE', 'default')

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


require_apikey = decorator_from_middleware(SimpleKeyMiddleware)
