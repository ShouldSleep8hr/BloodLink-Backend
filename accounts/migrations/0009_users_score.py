# Generated by Django 5.1 on 2025-01-29 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_users_full_name_users_line_username_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
