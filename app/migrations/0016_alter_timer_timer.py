# Generated by Django 5.0.2 on 2024-06-18 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_timer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timer',
            name='timer',
            field=models.IntegerField(default=0),
        ),
    ]
