# Generated by Django 3.1.3 on 2020-12-07 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0026_auto_20201207_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='students_test',
            field=models.ManyToManyField(to='tests.Test'),
        ),
    ]
