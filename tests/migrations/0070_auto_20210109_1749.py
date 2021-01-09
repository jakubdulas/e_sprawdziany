# Generated by Django 3.1.3 on 2021-01-09 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0026_auto_20210105_1354'),
        ('tests', '0069_auto_20210109_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='true_false',
        ),
        migrations.AlterField(
            model_name='grade',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='teacher.teacher'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='test',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.test'),
        ),
    ]
