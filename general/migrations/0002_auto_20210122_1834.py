# Generated by Django 3.1.3 on 2021-01-22 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=128)),
                ('phone_number', models.CharField(max_length=12)),
            ],
        ),
        migrations.DeleteModel(
            name='JoiningApplication',
        ),
    ]