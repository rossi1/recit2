# Generated by Django 2.0 on 2019-02-01 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20190201_0606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessinfo',
            name='business_name',
            field=models.CharField(max_length=250),
        ),
    ]
