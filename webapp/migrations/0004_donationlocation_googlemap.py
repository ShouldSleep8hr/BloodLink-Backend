# Generated by Django 5.1 on 2024-09-08 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_donationlocation_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationlocation',
            name='googlemap',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
