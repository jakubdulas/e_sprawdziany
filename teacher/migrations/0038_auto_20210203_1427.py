# Generated by Django 3.1.3 on 2021-02-03 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0037_school_join_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='name',
        ),
        migrations.RemoveField(
            model_name='class',
            name='school',
        ),
    ]
