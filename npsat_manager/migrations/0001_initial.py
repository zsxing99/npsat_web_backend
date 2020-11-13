# Generated by Django 3.1.3 on 2020-11-13 21:44

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import npsat_manager.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('caml_code', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('swat_code', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('crop_type', models.PositiveSmallIntegerField(choices=[(0, 'SWAT'), (1, 'GNLM'), (2, 'BOTH'), (3, 'Special identifier of all other crops')])),
                ('active_in_mantis', models.BooleanField(default=True)),
                ('similar_crops', models.ManyToManyField(blank=True, related_name='similar_backward', to='npsat_manager.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='MantisServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=255)),
                ('port', models.PositiveSmallIntegerField(default=1234)),
                ('online', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ModelRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[(0, 'not ready'), (1, 'ready'), (2, 'running'), (3, 'completed'), (4, 'error')], default=0)),
                ('status_message', models.CharField(blank=True, default='', max_length=2048, null=True)),
                ('result_values', models.TextField(blank=True, default='', null=True, validators=[django.core.validators.int_list_validator])),
                ('date_submitted', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('date_completed', models.DateTimeField(blank=True, null=True)),
                ('unsaturated_zone_travel_time', models.DecimalField(blank=True, decimal_places=8, max_digits=18, null=True)),
                ('n_years', models.IntegerField(blank=True, default=100)),
                ('reduction_start_year', models.IntegerField(blank=True, default=2020)),
                ('reduction_end_year', models.IntegerField(blank=True, default=2025)),
                ('water_content', models.DecimalField(decimal_places=4, default=0, max_digits=5)),
                ('n_wells', models.IntegerField(blank=True, null=True)),
                ('public', models.BooleanField(default=False)),
                ('is_base', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mantis_id', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=255)),
                ('active_in_mantis', models.BooleanField(default=True)),
                ('geometry', npsat_manager.models.SimpleJSONField(blank=True, null=True)),
                ('external_id', models.CharField(blank=True, max_length=255, null=True)),
                ('region_type', models.PositiveSmallIntegerField(choices=[(0, 'Central Valley'), (1, 'Basin'), (2, 'CVHMFarm'), (3, 'b118 basins'), (4, 'County'), (5, 'Townships'), (6, 'C2VsimSubregions')])),
            ],
        ),
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('active_in_mantis', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('scenario_type', models.PositiveSmallIntegerField(choices=[(1, 'flowScen'), (2, 'unsatScen'), (3, 'loadScen')])),
                ('crop_code_field', models.CharField(blank=True, choices=[(0, 'caml_code'), (1, 'swat_code')], max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultPercentile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentile', models.IntegerField()),
                ('values', npsat_manager.models.SimpleJSONField()),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='npsat_manager.modelrun')),
            ],
        ),
        migrations.AddField(
            model_name='modelrun',
            name='flow_scenario',
            field=models.ForeignKey(limit_choices_to={'scenario_type': 1}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='model_runs_flow', to='npsat_manager.scenario'),
        ),
        migrations.AddField(
            model_name='modelrun',
            name='load_scenario',
            field=models.ForeignKey(limit_choices_to={'scenario_type': 3}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='model_runs_load', to='npsat_manager.scenario'),
        ),
        migrations.AddField(
            model_name='modelrun',
            name='regions',
            field=models.ManyToManyField(related_name='model_runs', to='npsat_manager.Region'),
        ),
        migrations.AddField(
            model_name='modelrun',
            name='unsat_scenario',
            field=models.ForeignKey(limit_choices_to={'scenario_type': 2}, on_delete=django.db.models.deletion.DO_NOTHING, related_name='model_runs_unsat', to='npsat_manager.scenario'),
        ),
        migrations.AddField(
            model_name='modelrun',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='model_runs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CropGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(max_length=255)),
                ('crops', models.ManyToManyField(related_name='groups', to='npsat_manager.Crop')),
            ],
        ),
        migrations.CreateModel(
            name='Modification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proportion', models.DecimalField(decimal_places=4, max_digits=5)),
                ('crop', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='modifications', to='npsat_manager.crop')),
                ('model_run', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='npsat_manager.modelrun')),
            ],
            options={
                'unique_together': {('model_run', 'crop')},
            },
        ),
        migrations.AddConstraint(
            model_name='modelrun',
            constraint=models.UniqueConstraint(condition=models.Q(is_base=True), fields=('flow_scenario', 'load_scenario', 'unsat_scenario'), name='unique_base_model_scenario'),
        ),
    ]
