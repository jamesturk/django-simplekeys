import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):
    help = 'Export API usage report.'

    def add_arguments(self, parser):
        parser.add_argument('--days', dest='days', default=7, help='days of usage to export')

    def handle(self, *args, **options):

        backend = getattr(settings, 'SIMPLEKEYS_RATE_LIMIT_BACKEND',
                          'simplekeys.backends.CacheBackend')
        backend = import_string(backend)()

        dw = csv.writer(self.stdout)
        dw.writerow(('key', 'zone', 'date', 'requests'))

        for key, date_zone_num in backend.get_usage(days=int(options['days'])).items():
            for date, zone_num in date_zone_num.items():
                for zone, requests in zone_num.items():
                    dw.writerow((key, zone, date, requests))
