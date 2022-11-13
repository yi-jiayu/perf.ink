# Generated by Django 4.1.2 on 2022-11-13 04:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0013_salmonrunwave_salmonrunshiftplayer_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="salmonrunshiftsummary",
            name="rotation",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shifts",
                to="app.salmonrunrotation",
            ),
        ),
    ]
