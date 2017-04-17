import time
from django.test import TestCase

from .models import Tier, Zone, Key, QUOTA_DAILY
from .verifier import VerificationError, verify, RateLimitError, backend


class UsageTestCase(TestCase):
    def setUp(self):
        self.bronze = Tier.objects.create(slug='bronze', name='Bronze')
        self.gold = Tier.objects.create(slug='gold', name='Gold')
        self.default_zone = Zone.objects.create(slug='default', name='Default')
        self.premium_zone = Zone.objects.create(slug='premium', name='Premium')
        self.secret_zone = Zone.objects.create(slug='secret', name='Secret')

        # only available on memory backend
        backend.reset()

        self.bronze.limits.create(
            zone=self.default_zone,
            quota_requests=100,
            quota_period=QUOTA_DAILY,
            requests_per_second=2,
            burst_size=10,
        )
        self.bronze.limits.create(
            zone=self.premium_zone,
            quota_requests=10,
            quota_period=QUOTA_DAILY,
            requests_per_second=1,
            burst_size=2,
        )

        self.gold.limits.create(
            zone=self.default_zone,
            quota_requests=1000,
            quota_period=QUOTA_DAILY,
            requests_per_second=5,
            burst_size=10,
        )
        self.gold.limits.create(
            zone=self.premium_zone,
            quota_requests=100,
            quota_period=QUOTA_DAILY,
            requests_per_second=1,
            burst_size=2,
        )
        self.gold.limits.create(
            zone=self.secret_zone,
            quota_requests=100,
            quota_period=QUOTA_DAILY,
            requests_per_second=1,
            burst_size=2,
        )

        Key.objects.create(
            key='bronze1',
            status='a',
            tier=self.bronze,
            email='bronze1@example.com',
        )
        Key.objects.create(
            key='bronze2',
            status='a',
            tier=self.bronze,
            email='bronze2@example.com',
        )
        Key.objects.create(
            key='gold',
            status='a',
            tier=self.gold,
            email='gold@example.com',
        )

    def test_verifier_bad_key(self):
        self.assertRaises(VerificationError, verify, 'badkey', 'bronze')

    def test_verifier_inactive_key(self):
        Key.objects.create(
            key='newkey',
            status='u',
            tier=self.gold,
            email='new@example.com',
        )
        self.assertRaises(VerificationError, verify, 'newkey', 'bronze')

    def test_verifier_suspended_key(self):
        Key.objects.create(
            key='badactor',
            status='s',
            tier=self.gold,
            email='new@example.com',
        )
        self.assertRaises(VerificationError, verify, 'badactor', 'bronze')

    def test_verifier_zone_access(self):
        # gold has access, bronze doesn't
        self.assert_(verify('gold', 'secret'))
        self.assertRaises(VerificationError, verify, 'bronze1', 'secret')

    def test_verifier_rate_limit(self):
        # to start - we should have full capacity for a burst of 10
        for x in range(10):
            verify('bronze1', 'default')

        # this next one should raise an exception
        self.assertRaises(RateLimitError, verify, 'bronze1', 'default')

        # let's wait one second, this will let the bucket get two more tokens
        time.sleep(1)

        # two more, then limited
        verify('bronze1', 'default')
        verify('bronze1', 'default')
        self.assertRaises(RateLimitError, verify, 'bronze1', 'default')

    def test_verifier_rate_limit_full_refill(self):
        # let's use the premium zone now - 1req/sec. & burst of 2
        verify('bronze1', 'premium')
        verify('bronze1', 'premium')
        self.assertRaises(RateLimitError, verify, 'bronze1', 'premium')

        # in three seconds - ensure we haven't let capacity surpass burst rate
        time.sleep(3)
        verify('bronze1', 'premium')
        verify('bronze1', 'premium')
        self.assertRaises(RateLimitError, verify, 'bronze1', 'premium')

    def test_verifier_rate_limit_key_dependent(self):
        # ensure that the rate limit is unique per-key

        # each key is able to get both of its requests in, no waiting
        verify('bronze1', 'premium')
        verify('bronze1', 'premium')
        verify('bronze2', 'premium')
        verify('bronze2', 'premium')

        self.assertRaises(RateLimitError, verify, 'bronze1', 'premium')
        self.assertRaises(RateLimitError, verify, 'bronze2', 'premium')


    def test_verifier_rate_limit_zone_dependent(self):
        # ensure that the rate limit is unique per-zone

        # key is able to get both of its requests in, no waiting
        verify('bronze1', 'premium')
        verify('bronze1', 'premium')
        # and can hit another zone no problem
        verify('bronze1', 'default')

        # but premium is still exhausted
        self.assertRaises(RateLimitError, verify, 'bronze1', 'premium')
