# Generated by Django 5.0.2 on 2024-06-28 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_alter_patient_assignments_total_minute_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='remaining_seconds',
            field=models.IntegerField(default=60),
        ),
    ]
