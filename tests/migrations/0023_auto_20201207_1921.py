# Generated by Django 3.1.3 on 2020-12-07 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0009_delete_student'),
        ('tests', '0022_auto_20201207_1804'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Test',
            new_name='BlankTest',
        ),
    ]
