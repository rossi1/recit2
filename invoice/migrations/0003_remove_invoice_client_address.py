# Generated by Django 2.0 on 2019-03-14 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20190313_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='client_address',
        ),
    ]
