# Generated by Django 3.1.3 on 2021-01-04 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0017_auto_20210104_1413'),
        ('student', '0004_auto_20210104_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='school',
        ),
        migrations.AddField(
            model_name='student',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.school'),
        ),
    ]