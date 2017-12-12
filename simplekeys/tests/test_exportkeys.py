import csv
from django.test import TestCase
from django.test.utils import captured_stdout
from django.core.management import call_command
from ..models import Tier, Key


class ExportKeysTestCase(TestCase):

    def setUp(self):
        self.bronze = Tier.objects.create(slug='bronze', name='Bronze')
        self.gold = Tier.objects.create(slug='gold', name='Gold')

        Key.objects.create(key='one', status='a', tier=self.bronze,
                           email='one@example.com', name='User One')
        Key.objects.create(key='two', status='a', tier=self.gold,
                           email='two@example.com', name='User Two')
        Key.objects.create(key='three', status='u', tier=self.bronze,
                           email='three@example.com', name='User Three')
        Key.objects.create(key='four', status='a', tier=self.gold,
                           email='four@example.com', name='User Four')

    def test_basic_export(self):
        with captured_stdout() as stdout:
            call_command('exportkeys')

            stdout.seek(0)

            data = list(csv.DictReader(stdout))
            self.assertEquals(len(data), 4)
            self.assertEquals(data[0]['key'], 'one')
            self.assertEquals(data[1]['tier'], 'Gold')
            self.assertEquals(data[2]['status'], 'u')
            self.assertEquals(data[3]['email'], 'four@example.com')

    def test_export_flags(self):
        offset = Key.objects.all().order_by('created_at')[1]

        with captured_stdout() as stdout:
            call_command('exportkeys', '--since=' + offset.created_at.isoformat())
            stdout.seek(0)
            data = list(csv.DictReader(stdout))
            self.assertEquals(len(data), 3)
