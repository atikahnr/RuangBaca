# Generated by Django 2.1b1 on 2019-02-18 07:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0020_transaksipemesanan_tenggat_waktu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaksipemesanan',
            name='tenggat_waktu',
            field=models.DateField(default=datetime.datetime(2019, 2, 18, 14, 57, 43, 659469)),
        ),
    ]