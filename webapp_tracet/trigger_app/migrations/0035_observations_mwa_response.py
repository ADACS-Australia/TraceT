# Generated by Django 4.0.4 on 2023-08-03 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trigger_app", "0034_rename_event_group_id_observations_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="observations",
            name="mwa_response",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
