import csv
from django.core.management.base import BaseCommand
from ...models import Key


class Command(BaseCommand):
    help = 'Export API user information.'

    def add_arguments(self, parser):
        parser.add_argument('--since', dest='since', default=False,
                            help='only dump users since a given date')

    def handle(self, *args, **options):
        fields = ('key', 'status', 'tier', 'email', 'name', 'organization', 'usage', 'website',
                  'created_at', 'updated_at')

        dw = csv.DictWriter(self.stdout, fields)
        dw.writeheader()

        for key in Key.objects.all().order_by('created_at'):
            dw.writerow({f: getattr(key, f) for f in fields})
