# Generated by Django 5.1 on 2025-01-26 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0025_achievement_announcement_event_eventparticipant_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='achievement',
            old_name='desciption',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='desciption',
            new_name='description',
        ),
    ]
