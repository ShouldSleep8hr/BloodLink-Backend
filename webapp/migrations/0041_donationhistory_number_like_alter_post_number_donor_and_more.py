# Generated by Django 5.1 on 2025-02-19 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0040_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationhistory',
            name='number_like',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='number_donor',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='number_interest',
            field=models.IntegerField(default=0),
        ),
    ]
