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

        qs = Key.objects.all()

        if options['since']:
            qs = qs.filter(created_at__gte=options['since'])

        for key in qs.order_by('created_at'):
            dw.writerow({f: getattr(key, f) for f in fields})
