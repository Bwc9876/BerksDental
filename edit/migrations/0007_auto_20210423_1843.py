# Generated by Django 3.1.7 on 2021-04-23 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0006_officer_role'),
    ]

    operations = [
        migrations.RenameField(
            model_name='officer',
            old_name='role',
            new_name='title',
        ),
    ]