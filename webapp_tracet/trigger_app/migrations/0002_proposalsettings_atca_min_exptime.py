# Generated by Django 4.0.4 on 2022-07-14 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposalsettings',
            name='atca_min_exptime',
            field=models.IntegerField(default=30, help_text='Minimum total exposure time of all the observations combined for the observation to be viable. If this amount of time is not available, the observation will not be scheduled.', verbose_name='Minimum Exposure Time (mins)'),
        ),
    ]
