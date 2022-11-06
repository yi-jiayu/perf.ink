# Generated by Django 4.1.2 on 2022-11-06 03:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0010_alter_salmonrunshiftsummaryraw_played_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalmonRunShiftSummary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("splatnet_id", models.TextField()),
                ("played_at", models.DateTimeField()),
                ("waves_cleared", models.IntegerField()),
                ("grade", models.TextField()),
                ("grade_points", models.IntegerField()),
                ("grade_point_diff", models.TextField()),
                ("golden_eggs_delivered_team", models.IntegerField()),
                ("power_eggs_delivered_team", models.IntegerField()),
                ("golden_eggs_delivered_self", models.IntegerField()),
                ("power_eggs_delivered_self", models.IntegerField()),
                ("king_salmonid", models.TextField()),
                ("king_salmonid_defeated", models.BooleanField()),
                (
                    "rotation",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.salmonrunrotation",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="salmonrunshiftsummary",
            constraint=models.UniqueConstraint(
                fields=("splatnet_id", "uploaded_by"),
                name="salmonrunshiftsummary_unique",
            ),
        ),
    ]
