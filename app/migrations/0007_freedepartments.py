# Generated by Django 5.0.6 on 2024-06-05 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_busydepartments_delete_freedepartments'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeDepartments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
