# Generated by Django 3.1.3 on 2021-03-25 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0081_auto_20210325_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_headmaster',
            field=models.BooleanField(null=True),
        ),
    ]
