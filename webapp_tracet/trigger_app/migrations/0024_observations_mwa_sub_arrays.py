# Generated by Django 4.0.4 on 2023-06-11 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trigger_app", "0023_alter_cometlog_log_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="observations",
            name="mwa_sub_arrays",
            field=models.JSONField(null=True),
        ),
    ]
