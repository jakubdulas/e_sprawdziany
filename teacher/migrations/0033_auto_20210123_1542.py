# Generated by Django 3.1.3 on 2021-01-23 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0032_schoolterm'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='number',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacher.school')),
            ],
        ),
        migrations.AddField(
            model_name='schoolterm',
            name='school_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.schoolyear'),
        ),
    ]
