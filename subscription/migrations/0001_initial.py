# Generated by Django 2.0 on 2019-03-27 23:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_freemium', models.BooleanField(default=True)),
                ('is_freelancing', models.BooleanField(default=False)),
                ('is_buisness', models.BooleanField(default=False)),
                ('plan_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_plan', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
