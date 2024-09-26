# Generated by Django 5.1 on 2024-09-18 08:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linemessagingapi', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='linechannel',
            name='bot_id',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='linechannelcontact',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='line_channel_contacts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='linechannel',
            name='channel_access_token',
            field=models.TextField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='linechannelcontact',
            name='contact_id',
            field=models.CharField(db_index=True, max_length=50, unique=True),
        ),
    ]
