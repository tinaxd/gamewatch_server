# Generated by Django 4.2.5 on 2023-09-24 09:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ow2db_web", "0006_alter_ow2uniqueuser_last_seen_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ow2uniqueuser",
            name="username",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]