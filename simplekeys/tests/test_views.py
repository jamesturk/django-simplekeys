from django.test import TestCase
from django.core import mail
from ..models import Tier, Zone, Key
from ..verifier import backend
from ..views import _get_confirm_hash


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
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(len(key.key), 36)     # default is UUID
        self.assertIn(key.key, str(mail.outbox[0].message()))

        # ensure redirect to / (OK that it is a 404)
        self.assertRedirects(response, '/', target_status_code=404)

    def test_invalid_post(self):
        # invalid post - missing email
        response = self.client.post('/register/',
                                    {'name': 'Amy',
                                     }
                                    )

        # response should be the page w/ errors on the form
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['form'].errors), 1)

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


class ConfirmationViewTestCase(TestCase):

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
        self.key = 'sample'
        self.email = 'amy@example.com'
        self.key_obj = Key.objects.create(status='u', key=self.key,
                                          email=self.email,
                                          tier=default_tier
                                          )
        self.hash = _get_confirm_hash(self.key, self.email)

    def test_get(self):
        response = self.client.get(
            '/confirm/?key={}&email={}&confirm_hash={}'.format(
                self.key, self.email, self.hash
            )
        )
        # get a response pointing us towards a POST to the same data
        self.assertEquals(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn(self.key, response.content.decode())
        self.assertIn(self.email, response.content.decode())
        self.assertIn(self.hash, response.content.decode())

    def test_get_invalid(self):
        response = self.client.get(
            '/confirm/?key={}&email={}'.format(
                self.key, self.email,
            )
        )
        # hash isn't checked on GET, but still must be present
        self.assertEquals(response.status_code, 400)

    def test_post(self):
        response = self.client.post('/confirm/',
                                    {'key': self.key,
                                     'email': self.email,
                                     'confirm_hash': self.hash})
        self.assertEquals(response.status_code, 200)
        self.assertIn(self.key, response.content.decode())
        # status is updated to active
        self.assertEquals(Key.objects.get(key=self.key).status, 'a')

    def test_post_invalid(self):
        response = self.client.post('/confirm/',
                                    {'key': self.key,
                                     'email': self.email,
                                     'confirm_hash': 'bad-hash'})
        self.assertEquals(response.status_code, 400)
        # status is unchanged
        self.assertEquals(Key.objects.get(key=self.key).status, 'u')

    def test_post_suspended_key(self):
        self.key_obj.status = 's'
        self.key_obj.save()
        response = self.client.post('/confirm/',
                                    {'key': self.key,
                                     'email': self.email,
                                     'confirm_hash': self.hash})
        # don't let them update a suspended key
        self.assertEquals(response.status_code, 400)
        self.assertEquals(Key.objects.get(key=self.key).status, 's')
