# Generated by Django 3.1.3 on 2021-01-22 23:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0026_auto_20210105_1354'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='school',
        ),
        migrations.AddField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.school'),
        ),
    ]