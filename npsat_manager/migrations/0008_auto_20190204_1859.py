# Generated by Django 2.1.1 on 2019-02-05 02:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('npsat_manager', '0007_auto_20190204_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelrun',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='model_runs', to=settings.AUTH_USER_MODEL),
        ),
    ]
