# Generated by Django 2.1b1 on 2019-01-31 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0003_auto_20181213_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='skripsi',
            name='abstrak',
            field=models.FileField(blank=True, upload_to='abstrak/'),
        ),
    ]
