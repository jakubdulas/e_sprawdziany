# Generated by Django 3.1.3 on 2021-01-04 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0019_auto_20210104_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headmaster',
            name='school',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.school'),
        ),
    ]
