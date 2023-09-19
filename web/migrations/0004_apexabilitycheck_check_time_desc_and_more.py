# Generated by Django 4.0.4 on 2022-05-01 02:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0003_auto_20220102_0000"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="apexabilitycheck",
            index=models.Index(fields=["-time"], name="check_time_desc"),
        ),
        migrations.AddIndex(
            model_name="levelupdate",
            index=models.Index(fields=["-time"], name="lu_time_desc"),
        ),
        migrations.AddIndex(
            model_name="rankupdate",
            index=models.Index(fields=["-time"], name="ru_time_desc"),
        ),
    ]
