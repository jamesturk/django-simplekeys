from django.test import TestCase
from django.core import mail
from ..models import Tier, Zone, Key
from ..verifier import backend


class RegistrationViewTestCase(TestCase):

    def setUp(self):
        backend.reset()

        default_zone = Zone.objects.create(slug='default', name='default')
        default_tier = Tier.objects.create(slug='default', name='default')
        default_tier.limits.create(
            zone=default_zone,
            quota_requests=10,
            quota_period='d',
            requests_per_second=2,
            burst_size=10,
        )
        Tier.objects.create(slug='special', name='special')

    def test_get(self):
        # ensure form is present
        response = self.client.get('/register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_valid_post(self):
        email = 'amy@example.com'
        response = self.client.post('/register/',
                                    {'email': email,
                                     'name': 'Amy',
                                     'organization': 'ACME'
                                     }
                                    )
        # ensure key is created
        key = Key.objects.get(email=email)
        self.assertEquals(key.email, email)
        self.assertEquals(key.name, 'Amy')
        self.assertEquals(key.organization, 'ACME')
        self.assertEquals(key.status, 'u')
        self.assertEquals(key.tier.slug, 'default')

        # ensure email is sent and contains key
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(key.key, str(mail.outbox[0].message()))

        # ensure redirect to / (OK that it is a 404)
        self.assertRedirects(response, '/', target_status_code=404)


    def test_invalid_post(self):
        # invalid post - missing fields
        response = self.client.post('/register/',
                                    {'name': 'Amy',
                                     }
                                    )

        # response should be the page w/ errors on the form
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['form'].errors), 2)

        # no email is sent
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Key.objects.count(), 0)

    def test_custom_tier(self):
        email = 'amy@example.com'
        self.client.post('/register-special/',   # tier overridden
                         {'email': email,
                          'name': 'Amy',
                          'organization': 'ACME'
                          }
                         )
        # ensure key is created in right tier
        key = Key.objects.get(email=email)
        self.assertEquals(key.tier.slug, 'special')

    def test_relative_confirmation_url(self):
        self.client.post('/register/',
                         {'email': 'amy@example.com',
                          'name': 'Amy',
                          'organization': 'ACME'
                          }
                         )
        # is built from Site URL and /confirm/
        confirmation_url = 'https://example.com/confirm/?'
        self.assertIn(confirmation_url, str(mail.outbox[0].message()))

    def test_absolute_confirmation_url(self):
        self.client.post('/register-special/',
                         {'email': 'amy@example.com',
                          'name': 'Amy',
                          'organization': 'ACME'
                          }
                         )
        # absolute URL
        confirmation_url = 'https://confirm.example.com/special-confirm/?'
        self.assertIn(confirmation_url, str(mail.outbox[0].message()))
