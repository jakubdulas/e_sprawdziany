# Generated by Django 3.1.3 on 2020-12-01 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0008_auto_20201129_1248'),
        ('tests', '0013_auto_20201130_1811'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('textarea', models.TextField(blank=True, null=True)),
                ('char_field', models.CharField(blank=True, max_length=128, null=True)),
                ('is_correct', models.BooleanField(blank=True, default=False, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacher.student')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.task')),
            ],
        ),
    ]
