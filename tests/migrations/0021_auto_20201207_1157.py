# Generated by Django 3.1.3 on 2020-12-07 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
        ('tests', '0020_auto_20201207_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student'),
        ),
    ]
