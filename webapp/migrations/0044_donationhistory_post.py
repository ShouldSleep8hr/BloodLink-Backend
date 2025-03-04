# Generated by Django 5.1 on 2025-03-04 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0043_remove_donationhistory_verify_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationhistory',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donations', to='webapp.post'),
        ),
    ]
