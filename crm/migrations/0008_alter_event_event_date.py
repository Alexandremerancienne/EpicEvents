# Generated by Django 3.2.5 on 2021-08-17 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0007_alter_event_event_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="event_date",
            field=models.DateTimeField(null=True),
        ),
    ]
