# Generated by Django 3.2.5 on 2021-08-17 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_rename_event_status_event_event_over'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_over',
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.BooleanField(),
        ),
    ]