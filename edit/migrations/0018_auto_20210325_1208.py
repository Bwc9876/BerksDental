# Generated by Django 3.1.7 on 2021-03-25 16:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0017_auto_20210324_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-dateOf', 'startTime', 'endTime']},
        ),
    ]