# Generated by Django 3.1.3 on 2020-12-23 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0043_test_is_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
