# Generated by Django 3.1.3 on 2021-02-19 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0093_auto_20210219_1156'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grade',
            name='is_final',
        ),
        migrations.RemoveField(
            model_name='grade',
            name='is_predicted',
        ),
    ]
