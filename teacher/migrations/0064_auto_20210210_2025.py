# Generated by Django 3.1.3 on 2021-02-10 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0063_lesson_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='slug',
            field=models.SlugField(null=True, unique=True),
        ),
    ]
