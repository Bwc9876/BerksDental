# Generated by Django 3.1.7 on 2021-03-22 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0013_auto_20210322_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryphoto',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
