# Generated by Django 2.0 on 2019-02-01 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20190131_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessinfo',
            name='cac_number',
            field=models.IntegerField(blank=True),
        ),
    ]
