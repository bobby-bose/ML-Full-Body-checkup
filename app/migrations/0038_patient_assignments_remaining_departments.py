# Generated by Django 5.0.2 on 2024-06-28 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_remove_patient_progress_bar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient_assignments',
            name='remaining_departments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
