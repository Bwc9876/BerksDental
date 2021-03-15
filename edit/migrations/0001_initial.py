# Generated by Django 3.1.7 on 2021-03-11 18:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('dateOf', models.DateField()),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ExternalLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('url', models.URLField(max_length=350)),
                ('display_name', models.CharField(max_length=100)),
                ('sort_order', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='GalleryPhoto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('picture', models.ImageField(upload_to='gallery-photos')),
                ('caption', models.CharField(max_length=1000)),
                ('date_posted', models.DateField(auto_now_add=True)),
                ('featured', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('picture', models.ImageField(upload_to='officer-photos')),
                ('biography', models.CharField(max_length=2000)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
