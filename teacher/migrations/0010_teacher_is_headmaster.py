# Generated by Django 3.1.3 on 2020-12-25 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0009_delete_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_headmaster',
            field=models.BooleanField(default=False),
        ),
    ]