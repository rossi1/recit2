# Generated by Django 2.0 on 2019-01-26 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20190125_0955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessinfo',
            name='business_logo',
        ),
        migrations.AddField(
            model_name='businessinfo',
            name='business_type',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
