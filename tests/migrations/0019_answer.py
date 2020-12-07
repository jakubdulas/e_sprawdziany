# Generated by Django 3.1.3 on 2020-12-07 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
        ('tests', '0018_delete_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('textarea', models.TextField(blank=True, null=True)),
                ('char_field', models.CharField(blank=True, max_length=128, null=True)),
                ('is_correct', models.BooleanField(blank=True, default=False, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.student')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.task')),
            ],
        ),
    ]