# Generated by Django 3.1.3 on 2021-01-05 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0025_auto_20210104_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ManyToManyField(blank=True, to='teacher.School'),
        ),
    ]
