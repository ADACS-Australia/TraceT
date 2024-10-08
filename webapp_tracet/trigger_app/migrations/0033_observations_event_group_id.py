# Generated by Django 4.0.4 on 2023-08-03 04:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("trigger_app", "0032_alter_observations_mwa_sky_map_pointings"),
    ]

    operations = [
        migrations.AddField(
            model_name="observations",
            name="event_group_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="trigger_app.event",
            ),
        ),
    ]
