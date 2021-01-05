# Generated by Django 3.1.3 on 2021-01-04 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0018_headmaster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='headmaster',
            name='user',
        ),
        migrations.AddField(
            model_name='headmaster',
            name='Teacher',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.teacher'),
        ),
    ]