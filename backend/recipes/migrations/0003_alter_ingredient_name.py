# Generated by Django 3.2.14 on 2023-06-25 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100, verbose_name='ингридиент'),
        ),
    ]
