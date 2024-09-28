# Generated by Django 5.1 on 2024-09-28 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0014_merge_20240928_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationlocation',
            name='facility_type',
            field=models.CharField(blank=True, choices=[('ร', 'โรงพยาบาล'), ('ศ', 'ศูนย์กาชาด'), ('ค', 'หน่วยรับบริจาคเคลื่อนที่')], max_length=50, null=True),
        ),
    ]
