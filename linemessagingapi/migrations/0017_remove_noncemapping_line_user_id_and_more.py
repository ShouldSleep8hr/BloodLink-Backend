# Generated by Django 5.1 on 2024-10-23 19:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linemessagingapi', '0016_rename_line_token_noncemapping_link_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='noncemapping',
            name='line_user_id',
        ),
        migrations.RemoveField(
            model_name='noncemapping',
            name='link_token',
        ),
    ]
