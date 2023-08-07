# Generated by Django 4.0.4 on 2023-08-03 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_app', '0035_observations_mwa_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposalsettings',
            name='testing',
            field=models.CharField(choices=[('PRETEND_REAL', 'Real events only (Pretend Obs)'), ('BOTH', 'Real events (Real Obs) and test events (Pretend Obs)'), ('REAL_ONLY', 'Real events only (Real Obs)')], default='REAL_ONLY', max_length=128, verbose_name='What events will this proposal trigger on?'),
        ),
    ]
