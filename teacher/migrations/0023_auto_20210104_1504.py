# Generated by Django 3.1.3 on 2021-01-04 14:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0022_teacher_is_headmaster'),
    ]

    operations = [
        migrations.RenameField(
            model_name='headmaster',
            old_name='Teacher',
            new_name='teacher',
        ),
    ]