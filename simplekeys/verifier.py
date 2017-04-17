from __future__ import division
from .models import Key, Limit
from .backends import MemoryBackend, RateLimitError


class VerificationError(Exception):
    pass


backend = MemoryBackend()


def verify(key, zone):
    # ensure we have a verified key w/ access to the zone
    try:
        # could also do this w/ new subquery expressions in 1.11
        kobj = Key.objects.get(key=key, status='a')
        limit = Limit.objects.get(tier=kobj.tier, zone__slug=zone)
    except Key.DoesNotExist:
        raise VerificationError('no valid key')
    except Limit.DoesNotExist:
        raise VerificationError('key does not have access to zone')

    # enforce rate limiting - will raise RateLimitError if exhausted
    kz = (key, zone)
    backend.get_token(kz, limit.requests_per_second, limit.burst_size)

    # TODO: enforce overall quota

    return True
