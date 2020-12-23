# Generated by Django 3.1.3 on 2020-11-30 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_auto_20201129_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeOfTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='task',
            name='type',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.typeoftask'),
        ),
    ]