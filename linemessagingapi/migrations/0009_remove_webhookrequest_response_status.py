# Generated by Django 5.1 on 2024-09-25 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('linemessagingapi', '0008_webhookrequest_response_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webhookrequest',
            name='response_status',
        ),
    ]
