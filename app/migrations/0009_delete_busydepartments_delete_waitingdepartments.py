# Generated by Django 5.0.6 on 2024-06-05 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_waitingdepartments_delete_freedepartments'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BusyDepartments',
        ),
        migrations.DeleteModel(
            name='WaitingDepartments',
        ),
    ]
