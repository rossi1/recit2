# Generated by Django 2.0 on 2019-05-15 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryproducts',
            name='is_avaliable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='inventoryproducts',
            name='weight',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
