# Generated by Django 5.0.2 on 2024-06-25 21:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_remove_patient_waiting_department_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Occupied_Departments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('oncurepackage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='occupied_departments_package', to='app.oncurepackages')),
            ],
        ),
        migrations.CreateModel(
            name='Patient_Assignments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_patient_assignments', to='app.oncurepackages')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_assignments', to='app.patient')),
                ('waiting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waiting_patient_assignments', to='app.oncurepackages')),
            ],
        ),
    ]
