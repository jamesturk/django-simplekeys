from django.conf import settings
from functools import wraps
from .verifier import verify_request


def key_required(zone=None):
    if not zone:
        zone = getattr(settings, 'SIMPLEKEYS_DEFAULT_ZONE', 'default')

    def decorator(func):
        @wraps
        def newfunc(request, *args, **kwargs):
            resp = verify_request(request, zone)
            if not resp:
                func(request, *args, **kwargs)
        return newfunc

    return decorator
