# Generated by Django 3.1.7 on 2021-04-17 20:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('edit', '0003_auto_20210417_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryphoto',
            name='picture',
            field=models.ImageField(height_field='height', upload_to='gallery-photos', width_field='width'),
        ),
        migrations.AlterField(
            model_name='officer',
            name='picture',
            field=models.ImageField(height_field='height', upload_to='officer-photos', width_field='width'),
        ),
    ]
