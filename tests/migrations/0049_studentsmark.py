# Generated by Django 3.1.3 on 2020-12-27 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
        ('tests', '0048_auto_20201227_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentsMark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.IntegerField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
                ('test', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.test')),
            ],
        ),
    ]
