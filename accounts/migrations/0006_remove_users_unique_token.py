# Generated by Django 5.1 on 2024-10-22 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_users_unique_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='unique_token',
        ),
    ]
