# Generated by Django 3.1.7 on 2021-03-15 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0004_auto_20210315_1406'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='externallink',
            options={'ordering': ['sort_order']},
        ),
        migrations.AlterField(
            model_name='externallink',
            name='sort_order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]