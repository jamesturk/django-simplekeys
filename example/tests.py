from django.test import TestCase, Client
from simplekeys.models import Tier, Zone, Key
from simplekeys.verifier import backend


class MiddlewareTestCase(TestCase):

    def setUp(self):
        backend.reset()

        self.bronze = Tier.objects.create(slug='bronze', name='Bronze')
        self.default_zone = Zone.objects.create(slug='default', name='Default')
        self.bronze.limits.create(
            zone=self.default_zone,
            quota_requests=10,
            quota_period='d',
            requests_per_second=2,
            burst_size=10,
        )
        Key.objects.create(
            key='bronze',
            status='a',
            tier=self.bronze,
            email='bronze1@example.com',
        )

    def test_view_no_key(self):
        response = self.client.get('/example/')
        self.assertEquals(response.status_code, 403)

    def test_view_key_header(self):
        response = self.client.get('/example/', HTTP_X_API_KEY='bronze')
        self.assertEquals(response.status_code, 200)

    def test_view_key_param(self):
        response = self.client.get('/example/?apikey=bronze')
        self.assertEquals(response.status_code, 200)

    def test_view_key_429(self):
        for x in range(10):
            response = self.client.get('/example/?apikey=bronze')
            self.assertEquals(response.status_code, 200)
        # 11th request, exceeds burst
        response = self.client.get('/example/?apikey=bronze')
        self.assertEquals(response.status_code, 429)

    # we won't test everything else, verifier tests take care of that
