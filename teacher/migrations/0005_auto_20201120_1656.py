# Generated by Django 3.1.3 on 2020-11-20 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0004_auto_20201120_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.school'),
        ),
    ]
