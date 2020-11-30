# Generated by Django 3.1.3 on 2020-11-30 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0008_auto_20201129_1248'),
        ('tests', '0012_auto_20201130_1808'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='students',
        ),
        migrations.AddField(
            model_name='test',
            name='students',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.class'),
        ),
    ]
