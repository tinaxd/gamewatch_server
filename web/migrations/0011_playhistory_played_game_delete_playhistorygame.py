# Generated by Django 4.2.5 on 2023-10-14 08:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0010_auto_20231014_1108"),
    ]

    operations = [
        migrations.AddField(
            model_name="playhistory",
            name="played_game",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="web.game",
            ),
        ),
        migrations.DeleteModel(
            name="PlayHistoryGame",
        ),
    ]
