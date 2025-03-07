# Generated by Django 5.1 on 2025-01-29 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0027_remove_preferredarea_districts_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferredarea',
            name='district',
        ),
        migrations.RemoveField(
            model_name='preferredarea',
            name='subdistrict',
        ),
        migrations.AddField(
            model_name='preferredarea',
            name='districts',
            field=models.ManyToManyField(blank=True, related_name='preferred_areas', to='webapp.district'),
        ),
        migrations.AddField(
            model_name='preferredarea',
            name='provinces',
            field=models.ManyToManyField(blank=True, related_name='preferred_areas', to='webapp.province'),
        ),
    ]
