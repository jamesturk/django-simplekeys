import time
from collections import Counter
from django.conf import settings


class AbstractBackend(object):
    def get_tokens_and_timestamp(self, kz):
        """
            returns token_count, timestamp for kz

            if not found return (0, None)
        """
        raise NotImplementedError()

    def set_token_count(self, kz, tokens):
        """
            set counter for kz & timestamp to current time
        """
        raise NotImplementedError()

    def get_and_inc_quota_value(self, key, zone, quota_range):
        """
            increment & get quota value
            (value will increase regardless of validity)
        """
        raise NotImplementedError()


class MemoryBackend(AbstractBackend):
    def __init__(self):
        self.reset()

    def reset(self):
        self._counter = {}
        self._last_replenished = {}
        self._quota = Counter()

    def get_tokens_and_timestamp(self, key, zone):
        kz = (key, zone)
        return self._counter.get(kz, 0), self._last_replenished.get(kz)

    def set_token_count(self, key, zone, tokens):
        kz = (key, zone)
        self._last_replenished[kz] = time.time()
        self._counter[kz] = tokens

    def get_and_inc_quota_value(self, key, zone, quota_range):
        quota_key = '{}-{}-{}'.format(key, zone, quota_range)
        self._quota[quota_key] += 1
        return self._quota[quota_key]


class CacheBackend(AbstractBackend):
    def __init__(self):
        from django.core.cache import caches
        self.cache = caches[getattr(settings, 'SIMPLEKEYS_CACHE', 'default')]
        # 25 hour default, just longer than a day so that day limits are OK
        self.timeout = getattr(settings, 'SIMPLEKEYS_CACHE_TIMEOUT', 25*60*60)

    def get_tokens_and_timestamp(self, key, zone):
        kz = '{}-{}'.format(key, zone)
        # once we drop Django 1.8 support we can use
        # return self.cache.get_or_set(kz, (0, None), self.timeout)
        val = self.cache.get(kz)
        if val is None:
            val = self.cache.add(kz, (0, None), timeout=self.timeout)
            if val:
                return self.cache.get(kz)
        return val

    def set_token_count(self, key, zone, tokens):
        kz = '{}-{}'.format(key, zone)
        self.cache.set(kz, (tokens, time.time()), self.timeout)

    def get_and_inc_quota_value(self, key, zone, quota_range):
        quota_key = '{}-{}-{}'.format(key, zone, quota_range)
        # once we drop Django 1.8 support we can use
        # self.cache.get_or_set(quota_key, 0, timeout=self.timeout)
        if quota_key not in self.cache:
            self.cache.add(quota_key, 0, timeout=self.timeout)
        return self.cache.incr(quota_key)
