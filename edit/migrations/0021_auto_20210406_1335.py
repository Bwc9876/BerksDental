# Generated by Django 3.1.7 on 2021-04-06 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0020_event_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(default='No description provided', max_length=500),
        ),
    ]
