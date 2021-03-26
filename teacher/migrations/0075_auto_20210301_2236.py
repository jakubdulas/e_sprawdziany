# Generated by Django 3.1.3 on 2021-03-01 21:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0074_auto_20210301_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestforexcuse',
            name='school_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.schoolyear'),
        ),
        migrations.AddField(
            model_name='requestforexcuse',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.teacher'),
        ),
    ]