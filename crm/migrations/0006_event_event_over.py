# Generated by Django 3.2.5 on 2021-08-17 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0005_alter_contract_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="event_over",
            field=models.BooleanField(default=False),
        ),
    ]
