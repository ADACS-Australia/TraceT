# Generated by Django 4.0.4 on 2022-07-22 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trigger_app', '0005_rename_triggerid_eventgroup_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposaldecision',
            old_name='trigger_group_id',
            new_name='event_group_id',
        ),
        migrations.RenameField(
            model_name='voevent',
            old_name='trigger_group_id',
            new_name='event_group_id',
        ),
    ]
