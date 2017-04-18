import uuid
from django.db import models


QUOTA_PERIODS = (
    ('d', 'daily'),
    ('m', 'monthly'),
)


KEY_STATUSES = (
    ('u', 'Unactivated'),
    ('s', 'Suspended'),
    ('a', 'Active'),
)


class Tier(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Zone(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Limit(models.Model):
    tier = models.ForeignKey(Tier, related_name='limits')
    zone = models.ForeignKey(Zone, related_name='limits')
    quota_period = models.CharField(max_length=1, choices=QUOTA_PERIODS)
    quota_requests = models.PositiveIntegerField()
    requests_per_second = models.PositiveIntegerField()
    burst_size = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('tier', 'zone'),
        )


class Key(models.Model):
    key = models.CharField(max_length=40, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=1, choices=KEY_STATUSES)
    tier = models.ForeignKey(Tier, related_name='keys')

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} ({})'.format(self.email, self.key)

