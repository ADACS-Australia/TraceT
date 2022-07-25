# Generated by Django 4.0.4 on 2022-07-22 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_app', '0004_merge_20220722_0516'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TriggerID',
            new_name='EventGroup',
        ),
        migrations.RenameField(
            model_name='proposaldecision',
            old_name='trigger_id',
            new_name='trig_id',
        ),
        migrations.RenameField(
            model_name='voevent',
            old_name='trigger_id',
            new_name='trig_id',
        ),
        migrations.AlterField(
            model_name='proposalsettings',
            name='atca_band_15mm_exptime',
            field=models.IntegerField(default=60, help_text='Total exposure time of the observation cycle at this frequency band.', verbose_name='Band Exposure Time (mins)'),
        ),
        migrations.AlterField(
            model_name='proposalsettings',
            name='atca_band_16cm_exptime',
            field=models.IntegerField(default=60, help_text='Total exposure time of the observation cycle at this frequency band.', verbose_name='Band Exposure Time (mins)'),
        ),
        migrations.AlterField(
            model_name='proposalsettings',
            name='atca_band_3mm_exptime',
            field=models.IntegerField(default=60, help_text='Total exposure time of the observation cycle at this frequency band.', verbose_name='Band Exposure Time (mins)'),
        ),
        migrations.AlterField(
            model_name='proposalsettings',
            name='atca_band_4cm_exptime',
            field=models.IntegerField(default=60, help_text='Total exposure time of the observation cycle at this frequency band.', verbose_name='Band Exposure Time (mins)'),
        ),
        migrations.AlterField(
            model_name='proposalsettings',
            name='atca_band_7mm_exptime',
            field=models.IntegerField(default=60, help_text='Total exposure time of the observation cycle at this frequency band.', verbose_name='Band Exposure Time (mins)'),
        ),
    ]
