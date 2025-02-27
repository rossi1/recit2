# Generated by Django 2.0 on 2019-01-30 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_businessinfo_account_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='businessinfo',
            old_name='account_type',
            new_name='business_city',
        ),
        migrations.AddField(
            model_name='businessinfo',
            name='business_logo',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='businessinfo',
            name='business_state',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
