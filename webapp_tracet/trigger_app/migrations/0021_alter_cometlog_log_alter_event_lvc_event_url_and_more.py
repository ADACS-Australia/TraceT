# Generated by Django 4.0.4 on 2023-05-31 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trigger_app", "0020_remove_event_lvc_significance_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cometlog",
            name="log",
            field=models.CharField(blank=True, max_length=2027, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="lvc_event_url",
            field=models.CharField(blank=True, max_length=2025, null=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="lvc_skymap_fits",
            field=models.CharField(blank=True, max_length=2026, null=True),
        ),
        migrations.AlterField(
            model_name="observations",
            name="reason",
            field=models.CharField(blank=True, max_length=2029, null=True),
        ),
        migrations.AlterField(
            model_name="observations",
            name="website_link",
            field=models.URLField(max_length=2028),
        ),
    ]
