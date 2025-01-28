# Generated by Django 5.1 on 2025-01-28 22:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0026_rename_desciption_achievement_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferredarea',
            name='districts',
        ),
        migrations.RemoveField(
            model_name='preferredarea',
            name='provinces',
        ),
        migrations.RemoveField(
            model_name='preferredarea',
            name='subdistricts',
        ),
        migrations.AddField(
            model_name='preferredarea',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_areas', to='webapp.district'),
        ),
        migrations.AddField(
            model_name='preferredarea',
            name='subdistrict',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preferred_areas', to='webapp.subdistrict'),
        ),
    ]
