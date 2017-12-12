import csv
from django.test import TestCase, override_settings
from django.test.utils import captured_stdout
from django.core.management import call_command
from freezegun import freeze_time
from ..models import Tier, Key, Zone
from ..backends import CacheBackend


class UsageReportTestCase(TestCase):

    def setUp(self):
        b = CacheBackend()
        Zone.objects.create(slug='default', name='Default')
        Zone.objects.create(slug='special', name='Special')
        tier = Tier.objects.create(slug='default')
        Key.objects.create(key='key1', tier=tier, email='key1@example.com')
        Key.objects.create(key='key2', tier=tier, email='key2@example.com')

        # key, zone, day, num
        self.usage = (
            # Key 1 usage
            ('key1', 'default', '20170501', '20'),
            ('key1', 'default', '20170502', '200'),
            ('key1', 'default', '20170503', '20'),
            ('key1', 'special', '20170502', '5'),
            # Key 2 usage
            ('key2', 'special', '20170501', '1'),
            ('key2', 'special', '20170502', '1'),
            ('key2', 'special', '20170503', '1'),
        )

        for key, zone, day, num in self.usage:
            for _ in range(int(num)):
                b.get_and_inc_quota_value(key, zone, day)

    @override_settings(SIMPLEKEYS_RATE_LIMIT_BACKEND='simplekeys.backends.CacheBackend')
    def test_basic_report(self):
        with freeze_time('2017-05-05'):
            with captured_stdout() as stdout:
                call_command('usagereport')

                stdout.seek(0)

                data = tuple(tuple(row) for row in csv.reader(stdout))[1:]
                self.assertEquals(len(data), 7)
                self.assertEquals(set(data), set(self.usage))
