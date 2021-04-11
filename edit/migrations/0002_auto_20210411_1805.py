# Generated by Django 3.2 on 2021-04-11 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officer',
            name='name',
        ),
        migrations.AddField(
            model_name='officer',
            name='first_name',
            field=models.CharField(default='First', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='officer',
            name='last_name',
            field=models.CharField(default='Last', max_length=100),
            preserve_default=False,
        ),
    ]
