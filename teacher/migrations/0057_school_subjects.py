# Generated by Django 3.1.3 on 2021-02-10 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0056_lesson_replacement'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='subjects',
            field=models.ManyToManyField(null=True, to='teacher.Subject'),
        ),
    ]
