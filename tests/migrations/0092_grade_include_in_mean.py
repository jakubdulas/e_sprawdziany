# Generated by Django 3.1.3 on 2021-02-19 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0091_remove_test_mark'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='include_in_mean',
            field=models.BooleanField(default=True),
        ),
    ]