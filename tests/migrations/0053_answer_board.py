# Generated by Django 3.1.3 on 2021-01-01 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0052_auto_20201231_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='board',
            field=models.ImageField(blank=True, null=True, upload_to='boards/'),
        ),
    ]