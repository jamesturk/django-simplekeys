from django.db import models

QUOTA_DAILY = 60*60*24
QUOTA_MONTHLY = 60*60*24*30

QUOTA_PERIODS = (
    (QUOTA_DAILY, 'daily'),
    (QUOTA_MONTHLY, 'monthly'),
)


KEY_STATUSES = (
    ('u', 'Unactivated'),
    ('s', 'Suspended'),
    ('a', 'Active'),
)


class Tier(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)


class Zone(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)


class Limit(models.Model):
    tier = models.ForeignKey(Tier, related_name='limits')
    zone = models.ForeignKey(Zone, related_name='limits')
    quota_requests = models.PositiveIntegerField()
    quota_period = models.PositiveIntegerField(choices=QUOTA_PERIODS)
    requests_per_second = models.PositiveIntegerField()
    burst_size = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('tier', 'zone'),
        )


class Key(models.Model):
    key = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=1, choices=KEY_STATUSES)
    tier = models.ForeignKey(Tier, related_name='keys')

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
