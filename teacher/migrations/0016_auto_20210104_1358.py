# Generated by Django 3.1.3 on 2021-01-04 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0015_auto_20210104_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='school',
        ),
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ManyToManyField(to='teacher.School'),
        ),
    ]
