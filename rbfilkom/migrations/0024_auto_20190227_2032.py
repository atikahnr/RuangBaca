# Generated by Django 2.1b1 on 2019-02-27 13:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0023_auto_20190222_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='transaksipemesanan',
            name='tenggat_waktu',
            field=models.DateField(default=datetime.datetime(2019, 2, 27, 20, 32, 7, 232347)),
        ),
    ]