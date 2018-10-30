# Generated by Django 2.0.9 on 2018-10-30 00:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('simplekeys', '0002_auto_20170421_0307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='tier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='keys', to='simplekeys.Tier'),
        ),
    ]
