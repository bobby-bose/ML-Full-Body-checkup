# Generated by Django 5.0.2 on 2024-06-25 22:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_waiting_departments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='waiting_package',
        ),
        migrations.AddField(
            model_name='patient',
            name='waiting_department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiting_package', to='app.department'),
        ),
    ]
