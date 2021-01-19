# Generated by Django 3.1.3 on 2021-01-09 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0070_auto_20210109_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerForTF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked', models.BooleanField(blank=True)),
                ('is_correct', models.BooleanField(default=False)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.answer')),
                ('true_false', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.truefalsetask')),
            ],
        ),
    ]