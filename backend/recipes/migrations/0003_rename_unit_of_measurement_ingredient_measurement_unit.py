# Generated by Django 3.2.14 on 2023-06-20 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit_of_measurement',
            new_name='measurement_unit',
        ),
    ]