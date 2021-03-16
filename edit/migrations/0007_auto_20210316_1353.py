# Generated by Django 3.1.7 on 2021-03-16 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0006_auto_20210315_1753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='social',
            name='name',
        ),
        migrations.RemoveField(
            model_name='social',
            name='picture',
        ),
        migrations.AddField(
            model_name='social',
            name='service',
            field=models.CharField(choices=[('TW', 'Twitter'), ('IG', 'Instagram'), ('YT', 'YouTube'), ('FB', 'Facebook')], default='YT', max_length=2),
        ),
    ]