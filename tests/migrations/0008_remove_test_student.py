# Generated by Django 3.1.3 on 2020-11-30 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0007_remove_answeroption_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='student',
        ),
    ]
