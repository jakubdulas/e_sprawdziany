# Generated by Django 3.1.3 on 2021-04-08 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0082_teacher_is_headmaster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleelement',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='scheduleelement',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]