# Generated by Django 4.2.5 on 2023-10-14 01:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0007_game_emoji_name"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ApexabilityCheck",
            new_name="ApexabilityCheckOld",
        ),
        migrations.RenameIndex(
            model_name="apexabilitycheckold",
            new_name="check_time_old_desc",
            old_name="check_time_desc",
        ),
    ]
