# Generated by Django 3.1.3 on 2021-02-09 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0053_lesson_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='date',
            field=models.DateField(null=True),
        ),
    ]