# Generated by Django 2.0 on 2019-05-26 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_subscriptionplan_card_source'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='card_source',
        ),
    ]
