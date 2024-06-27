# Generated by Django 5.0.2 on 2024-06-24 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_patient_waiting_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='waiting_department',
        ),
        migrations.AddField(
            model_name='patient',
            name='waiting_package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiting_package', to='app.oncurepackages'),
        ),
    ]