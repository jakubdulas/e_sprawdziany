# Generated by Django 3.1.3 on 2020-12-11 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0029_task_correct_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='blanktest',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
