# Generated by Django 3.1.7 on 2021-03-19 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0009_auto_20210319_1309'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='officer',
            options={'ordering': ['sort_order']},
        ),
        migrations.AddField(
            model_name='officer',
            name='sort_order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='officer',
            name='biography',
            field=models.TextField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='officer',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True),
        ),
    ]
