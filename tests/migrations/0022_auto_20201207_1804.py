# Generated by Django 3.1.3 on 2020-12-07 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0021_auto_20201207_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.typeoftask'),
        ),
    ]
