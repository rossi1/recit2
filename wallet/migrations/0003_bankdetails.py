# Generated by Django 2.0 on 2019-01-30 16:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallet', '0002_carddetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=250)),
                ('bank_account_name', models.CharField(max_length=250)),
                ('bank_account_number', models.CharField(max_length=250)),
                ('bvn_number', models.CharField(max_length=250)),
                ('bank_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_details', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
