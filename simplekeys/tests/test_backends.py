from django.test import TestCase
from freezegun import freeze_time

from ..models import Zone, Key, Tier
from ..backends import MemoryBackend, CacheBackend


class MemoryBackendTestCase(TestCase):
    def get_backend(self):
        return MemoryBackend()

    def test_get_tokens_and_timestamp_initial(self):
        b = self.get_backend()
        self.assertEquals(b.get_tokens_and_timestamp('key', 'zone'), (0, None))

    def test_token_set_and_retrieve(self):
        b = self.get_backend()
        with freeze_time('2017-04-17'):
            b.set_token_count('key', 'zone', 100)
            tokens, timestamp = b.get_tokens_and_timestamp('key', 'zone')
            self.assertEquals(tokens, 100)
            self.assertEquals(int(timestamp), 1492387200)   # frozen time

    def test_key_and_zone_independence(self):
        b = self.get_backend()
        b.set_token_count('key', 'zone', 100)
        self.assertEquals(b.get_tokens_and_timestamp('key2', 'zone'),
                          (0, None))
        self.assertEquals(b.get_tokens_and_timestamp('key', 'zone2'),
                          (0, None))

    def test_get_and_inc_quota(self):
        b = self.get_backend()
        self.assertEquals(
            b.get_and_inc_quota_value('key', 'zone', '20170411'), 1
        )
        self.assertEquals(
            b.get_and_inc_quota_value('key', 'zone', '20170411'), 2
        )
        self.assertEquals(
            b.get_and_inc_quota_value('key', 'zone', '20170412'), 1
        )

    def test_get_and_inc_quota_key_and_zone_independence(self):
        b = self.get_backend()
        self.assertEquals(
            b.get_and_inc_quota_value('key', 'zone', '20170411'), 1
        )
        self.assertEquals(
            b.get_and_inc_quota_value('key2', 'zone', '20170411'), 1
        )
        self.assertEquals(
            b.get_and_inc_quota_value('key', 'zone2', '20170411'), 1
        )


class CacheBackendTestCase(MemoryBackendTestCase):
    """ do the same tests as MemoryBackendTestCase but w/ CacheBackend """

    def get_backend(self):
        # ensure we have a fresh cache backend each time
        c = CacheBackend()
        c.cache.clear()
        return c

    def test_get_usage(self):
        Zone.objects.create(slug='default', name='Default')
        Zone.objects.create(slug='special', name='Special')
        tier = Tier.objects.create(slug='default')
        Key.objects.create(key='key1', tier=tier, email='key1@example.com')
        Key.objects.create(key='key2', tier=tier, email='key2@example.com')
        b = self.get_backend()

        # key, zone, day, num
        usage = [
            # Key 1 usage
            ('key1', 'default', '20170501', 20),
            ('key1', 'default', '20170502', 200),
            ('key1', 'default', '20170503', 20),
            ('key1', 'special', '20170502', 5),
            # Key 2 usage
            ('key2', 'special', '20170501', 1),
            ('key2', 'special', '20170502', 1),
            ('key2', 'special', '20170503', 1),
        ]

        for key, zone, day, num in usage:
            for _ in range(num):
                b.get_and_inc_quota_value(key, zone, day)

        with freeze_time('2017-05-05'):
            key1usage = b.get_usage()['key1']
            assert key1usage['20170501']['default'] == 20
            assert key1usage['20170502']['default'] == 200
            assert key1usage['20170503']['default'] == 20
            assert key1usage['20170502']['special'] == 5
            assert key1usage['20170501']['special'] == 0

        # ensure we only get requested data
        with freeze_time('2017-05-15'):
            usage = b.get_usage(keys=['key1'], days=2)
            assert len(usage) == 1
            assert len(usage['key1']) == 2
