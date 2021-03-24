# Generated by Django 3.1.7 on 2021-03-23 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edit', '0014_auto_20210322_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='social',
            name='service',
            field=models.CharField(choices=[('TW', 'Twitter'), ('IG', 'Instagram'), ('YT', 'YouTube'), ('FB', 'Facebook'), ('LI', 'Linkedin'), ('PT', 'Pinterest'), ('EM', 'Email')], default='EM', max_length=2),
        ),
    ]
