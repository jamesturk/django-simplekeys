import time
from collections import Counter


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
