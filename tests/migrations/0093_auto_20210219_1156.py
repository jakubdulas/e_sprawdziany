# Generated by Django 3.1.3 on 2021-02-19 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0092_grade_include_in_mean'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='is_final',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='grade',
            name='is_predicted',
            field=models.BooleanField(default=False),
        ),
    ]
