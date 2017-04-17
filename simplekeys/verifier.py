from __future__ import division
import time
import datetime
from .models import Key, Limit
from .backends import MemoryBackend


class VerificationError(Exception):
    pass


class RateLimitError(Exception):
    pass


class QuotaError(Exception):
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
        raise VerificationError('key does not have access to zone {}'.format(
            zone
        ))

    # enforce rate limiting - will raise RateLimitError if exhausted
    # replenish first
    tokens, last_time = backend.get_tokens_and_timestamp(key, zone)

    if last_time is None:
        # if this is the first time, fill the bucket
        tokens = limit.burst_size
    else:
        # increment bucket, careful not to overfill
        tokens = min(
            tokens + (limit.requests_per_second * (time.time() - last_time)),
            limit.burst_size
        )

    # now try to decrement count
    if tokens >= 1:
        tokens -= 1
        backend.set_token_count(key, zone, tokens)
    else:
        raise RateLimitError('exhausted tokens {} req/sec, burst {}'.format(
            limit.requests_per_second, limit.burst_size
        ))

    # enforce daily/monthly quotas
    if limit.quota_period == 'd':
        quota_range = datetime.datetime.utcnow().strftime('%Y%m%d')
    elif limit.quota_period == 'm':
        quota_range = datetime.datetime.utcnow().strftime('%Y%m')

    if (backend.get_and_inc_quota_value(key, zone, quota_range) >
            limit.quota_requests):
        raise QuotaError('quota exceeded {}/{}'.format(
            limit.quota_requests, limit.get_quota_period_display()
        ))

    return True
