# Generated by Django 3.1.3 on 2021-02-09 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0052_lesson'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]