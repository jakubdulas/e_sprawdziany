# Generated by Django 3.1.3 on 2021-02-23 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directmessages', '0004_auto_20210119_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='directmessage',
            name='read_date',
            field=models.DateTimeField(null=True),
        ),
    ]
