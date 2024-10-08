# Generated by Django 4.0.4 on 2023-01-30 03:09

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trigger_app", "0007_event_self_generated_trig_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="lvc_binary_black_hole_probability",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_binary_neutron_star_probability",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_event_url",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_false_alarm_rate",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_includes_neutron_star_probability",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_neutron_star_black_hole_probability",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_prob_density_tile",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_retraction_message",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_significance",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_skymap_file",
            field=models.FileField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(
                    location="/home/dylan/development/TraceT/webapp_tracet/media//skymaps"
                ),
                upload_to="",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_skymap_fits",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="lvc_terrestial_probability",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="eventgroup",
            name="event_observed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="possibleeventassociation",
            name="event_observed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proposaldecision",
            name="alt",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proposaldecision",
            name="az",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="maximum_binary_black_hole_probability",
            field=models.FloatField(
                default=1, verbose_name="Maximum probability for event to be BBH"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="maximum_binary_neutron_star_probability",
            field=models.FloatField(
                default=1, verbose_name="Maximum probability for event to be BNS"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="maximum_neutron_star_black_hole_probability",
            field=models.FloatField(
                default=1, verbose_name="Maximum probability for event to be NSBH"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="maximum_neutron_star_probability",
            field=models.FloatField(
                default=1,
                help_text="PROB_NS - probability that at least one object in the binary has a mass that is less than 3 solar masses",
                verbose_name="Maximum on the probability that at least one object in the binary has a mass that is less than 3 solar masses",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="maximum_terrestial_probability",
            field=models.FloatField(
                default=0.95,
                help_text="Limit on the probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)",
                verbose_name="Maximum probability for event to be terrestial",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="minimum_binary_black_hole_probability",
            field=models.FloatField(
                default=0.0, verbose_name="Minimum probability for event to be BBH"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="minimum_binary_neutron_star_probability",
            field=models.FloatField(
                default=0.01, verbose_name="Minimum probability for event to be BNS"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="minimum_neutron_star_black_hole_probability",
            field=models.FloatField(
                default=0.01, verbose_name="Minimum probability for event to be NSBH"
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="minimum_neutron_star_probability",
            field=models.FloatField(
                default=0.01,
                help_text="PROB_NS - probability that at least one object in the binary has a mass that is less than 3 solar masses",
                verbose_name="Minimum on the probability that at least one object in the binary has a mass that is less than 3 solar masses",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="minimum_terrestial_probability",
            field=models.FloatField(
                default=0.0,
                help_text="Limit on the probability that the source is terrestrial (i.e., a background noise fluctuation or a glitch)",
                verbose_name="Minimum probability for event to be terrestial",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="observe_low_significance",
            field=models.BooleanField(
                default=True,
                help_text="2/day > FAR > (1/month CBC and 1/year BURST)",
                verbose_name="Observe events with low significance (high FAR)",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="observe_significant",
            field=models.BooleanField(
                default=True,
                help_text="(1/month CBC and 1/year BURST) > FAR",
                verbose_name="Observe events with high significance (low FAR)",
            ),
        ),
        migrations.AddField(
            model_name="proposalsettings",
            name="start_observation_at_high_sensitivity",
            field=models.BooleanField(
                default=True,
                help_text="On early warnings there will not be positional data so start MWA in sub array mode at the high sensitivity area over the indian ocean",
                verbose_name="Without positional data, start observations with MWA sub array at high sensitivity area",
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="trig_id",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="eventgroup",
            name="trig_id",
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name="proposaldecision",
            name="trig_id",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="proposalsettings",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("GRB", "Gamma-ray burst"),
                    ("FS", "Flare star"),
                    ("NU", "Neutrino"),
                    ("GW", "Gravitational wave"),
                ],
                max_length=3,
                verbose_name="What type of source will you trigger on?",
            ),
        ),
    ]
