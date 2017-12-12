import time
import itertools
import datetime
from collections import Counter
from django.conf import settings
from .models import Zone, Key


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

    def get_usage(self, keys=None, days=7):
        """
            get usage in a nested dictionary

            {
                api_key:  {
                    date: {
                        zone: N
                    }
                }
            }

            such that result['apikey']['20170501']['default'] is equal to the
            number of requests made by 'apikey' to 'default' zone endpoints on
            May 1, 2017.
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
        kz = '{}~{}'.format(key, zone)
        # once we drop Django 1.8 support we can use
        # return self.cache.get_or_set(kz, (0, None), self.timeout)
        val = self.cache.get(kz)
        if val is None:
            val = self.cache.add(kz, (0, None), timeout=self.timeout)
            if val:
                return self.cache.get(kz)
        return val

    def set_token_count(self, key, zone, tokens):
        kz = '{}~{}'.format(key, zone)
        self.cache.set(kz, (tokens, time.time()), self.timeout)

    def get_and_inc_quota_value(self, key, zone, quota_range):
        quota_key = '{}~{}~{}'.format(key, zone, quota_range)
        # once we drop Django 1.8 support we can use
        # self.cache.get_or_set(quota_key, 0, timeout=self.timeout)
        if quota_key not in self.cache:
            self.cache.add(quota_key, 0, timeout=self.timeout)
        return self.cache.incr(quota_key)

    def get_usage(self, keys=None, days=7):
        today = datetime.date.today()
        dates = [(today - datetime.timedelta(days=d)).strftime('%Y%m%d')
                 for d in range(days)]
        zones = Zone.objects.all().values_list('slug', flat=True)
        if not keys:
            keys = Key.objects.all().values_list('key', flat=True)
        all_keys = ['{}~{}~{}'.format(key, zone, date) for (key, zone, date) in
                    itertools.product(keys, zones, dates)]

        result = {k: {d: Counter() for d in dates} for k in keys}
        for cache_key, cache_val in self.cache.get_many(all_keys).items():
            key, zone, date = cache_key.split('~')
            result[key][date][zone] = cache_val

        return result
