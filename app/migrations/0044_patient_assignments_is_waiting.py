# Generated by Django 5.0.2 on 2024-06-29 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_alter_department_remaining_seconds'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient_assignments',
            name='is_waiting',
            field=models.BooleanField(default=False),
        ),
    ]
