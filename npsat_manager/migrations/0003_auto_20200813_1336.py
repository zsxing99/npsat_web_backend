# Generated by Django 3.0.7 on 2020-08-13 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('npsat_manager', '0002_auto_20200813_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelrun',
            name='regions',
            field=models.ManyToManyField(related_name='model_runs', to='npsat_manager.Region'),
        ),
    ]
