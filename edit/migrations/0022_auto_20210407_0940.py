# Generated by Django 3.1.7 on 2021-04-07 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0021_auto_20210406_1335'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-startDate', '-endDate']},
        ),
    ]