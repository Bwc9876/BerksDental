# Generated by Django 3.1.7 on 2021-04-17 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0002_auto_20210411_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryphoto',
            name='height',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='galleryphoto',
            name='width',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='officer',
            name='height',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='officer',
            name='width',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='galleryphoto',
            name='featured',
            field=models.BooleanField(default=False, help_text='This will determine whether to show this image on the home page (Max of 6)'),
        ),
        migrations.AlterField(
            model_name='galleryphoto',
            name='picture',
            field=models.ImageField(height_field=models.IntegerField(), upload_to='gallery-photos', width_field=models.IntegerField()),
        ),
        migrations.AlterField(
            model_name='officer',
            name='picture',
            field=models.ImageField(height_field=models.IntegerField(), upload_to='officer-photos', width_field=models.IntegerField()),
        ),
    ]
