# Generated by Django 3.2.5 on 2021-08-17 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_note_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_status',
            new_name='event_over',
        ),
    ]