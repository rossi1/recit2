# Generated by Django 2.0 on 2019-08-05 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_auto_20190804_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessinfo',
            name='business_name',
            field=models.CharField(editable=False, max_length=250),
        ),
    ]
