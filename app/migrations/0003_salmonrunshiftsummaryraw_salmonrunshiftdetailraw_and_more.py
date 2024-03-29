# Generated by Django 4.1.1 on 2022-10-16 07:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_splatnetsession_nintendosession"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalmonRunShiftSummaryRaw",
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
                ("shift_id", models.TextField()),
                ("data", models.JSONField()),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SalmonRunShiftDetailRaw",
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
                ("shift_id", models.TextField()),
                ("data", models.JSONField()),
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
            model_name="salmonrunshiftsummaryraw",
            constraint=models.UniqueConstraint(
                fields=("shift_id", "uploaded_by"),
                name="salmonrunshiftsummaryraw_unique",
            ),
        ),
        migrations.AddConstraint(
            model_name="salmonrunshiftdetailraw",
            constraint=models.UniqueConstraint(
                fields=("shift_id", "uploaded_by"),
                name="salmonrunshiftdetailraw_unique",
            ),
        ),
    ]
