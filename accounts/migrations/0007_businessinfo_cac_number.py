# Generated by Django 2.0 on 2019-01-30 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_businessinfo_approved_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessinfo',
            name='cac_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
