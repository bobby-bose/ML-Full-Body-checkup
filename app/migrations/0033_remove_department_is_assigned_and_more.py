# Generated by Django 5.0.2 on 2024-06-26 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_rename_is_occupied_department_is_assigned_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='is_assigned',
        ),
        migrations.RemoveField(
            model_name='department',
            name='is_waiting',
        ),
    ]
