# Generated by Django 2.0 on 2019-05-14 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryproducts',
            name='weight',
            field=models.CharField(max_length=50),
        ),
    ]
