# Generated by Django 5.0.2 on 2024-06-17 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_patientsecondmiddle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientsecondmiddle',
            name='hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='patientsecondmiddle',
            name='minutes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]