# Generated by Django 4.0.4 on 2023-11-17 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_app', '0039_proposalsettings_early_observation_time_seconds_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalsettings',
            name='early_observation_time_seconds',
            field=models.IntegerField(default=900, help_text='This is the observation time for early warning and preliminary notices, for MWA will use n=1'),
        ),
    ]
