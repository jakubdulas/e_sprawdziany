# Generated by Django 3.1.3 on 2021-02-18 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0086_auto_20210217_1759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grade',
            name='school_year',
        ),
    ]
